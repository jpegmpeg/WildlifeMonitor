"""
The purpose of this class is to create visual and audio detectors
such that when a videostream is passed through the detectors find and store relevant information 
"""


import numpy as np
#from concurrent.futures import ThreadPoolExecutor
import torch
import torch.nn.functional as F
import open_clip
from PIL import Image
from dataclasses import dataclass
from .environment import Environment
from .detection_unit import VideoDetection, AudioDetection, BoundingBox
from ultralytics import YOLO
from pathlib import Path
from .util.tracking_smoother import TrackClassSmoother
from pathlib import Path
from urllib.request import urlretrieve

#imports for audio
from transformers import pipeline
from .audio_environment import AudioEnvironment

TRACKER_CONFIG = Path(__file__).parent / "custom_botsort.yaml" #customization of the tracker paramters to see if i can opitmize animal detection.
MDV6_URL = "https://zenodo.org/records/15398270/files/MDV6-yolov10-c.pt?download=1"
CACHE = Path(__file__).parent  / ".cache" / "mdv6" / "MDV6-yolov10-c.pt"

def load_mdv6() -> YOLO:
    if not CACHE.exists():
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        urlretrieve(MDV6_URL, CACHE)
    return YOLO(str(CACHE))

def _pick_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"

@dataclass
class ModelConfig:
    yolo_conf: float = 0.3
    min_crop_size: int = 40
    bioclip_temperature: float = 2.0
    bioclip_min_exp: int = 100

class VisualDetector:
    """Class for detecting objects from the video, specifically animals"""

    def __init__(self, env: Environment, config: ModelConfig):
        #paramters for YOLO
        self.model = load_mdv6() #Use to use YOLOv8World for detect but switch for animal specificity 
        self.confidence = config.yolo_conf #sensitivity in prediciton, lower means more false positives
        #parameters for BioCLIP
        self.device = _pick_device()
        self.bio_model, _, self.bio_preprocess = open_clip.create_model_and_transforms("hf-hub:imageomics/bioclip-2")
        self.bio_tokenizer = open_clip.get_tokenizer("hf-hub:imageomics/bioclip-2")
        self.bio_model = self.bio_model.to(self.device).eval()
        self.labels = env.bioclip_labels() 
        self.to_common = env.reverse_map()
        self.min_crop_size = config.min_crop_size
        self.min_expand = config.bioclip_min_exp
        self.bioclip_temperature = config.bioclip_temperature


        #precompute text embedding so its dont at object intialization rather than each call
        with torch.no_grad():
            tokens = self.bio_tokenizer(self.labels).to(self.device)
            features = self.bio_model.encode_text(tokens)
            features = F.normalize(features, dim=-1) #normalize
        
        self.text_features = features  # shape: [num_classes, embed_dim]

        #util for labeling
        self.smooter = TrackClassSmoother() #meant to help keep consistent labels within a frame range for the same tracked entity 
    
    def _expand_small(self, x1, y1, x2, y2, w, h, img_w, img_h, min_size):
        """Bounding boxes can be extra small, in such case we should add more real pixels and expand for context"""
        #pad on both sides, so see amount needed to pad and halve to put on both ends
        pad_w = (min_size - w) / 2
        pad_h = (min_size - h) / 2
        #clip to image bounds
        nx1, ny1  = max(0, int(x1 - pad_w)), max(0, int(y1 - pad_h))
        nx2, ny2= min(img_w, int(x2 + pad_w)), min(img_h, int(y2 + pad_h))
        return nx1, ny1, nx2, ny2

    def _bio_classification(self, frame: np.ndarray, boxes_xyxy: list[tuple[float, float, float, float]]):
        """Second layer of CNN classification since YOLO does not perform well with specific species"""
        if not boxes_xyxy:
            return []
        
        # The current bgr for YOLO, CLIP works with rbg so convert
        frame_rgb = frame[:, :, ::-1]
        H, W = frame_rgb.shape[:2]

        tensors = []
        for x1, y1, x2, y2 in boxes_xyxy:
            #make sure the frame is bounded by image dimensions
            x1i, y1i = max(0, int(x1)), max(0, int(y1))
            x2i, y2i = min(W, int(x2)), min(H, int(y2))
            w, h = x2i - x1i, y2i - y1i #calculate bounding box size
            if w < self.min_crop_size or h < self.min_crop_size:
                x1i, y1i, x2i, y2i = self._expand_small(x1i, y1i, x2i, y2i, w, h, W, H, self.min_expand)
            crop = frame_rgb[y1i:y2i, x1i:x2i]
            pil = Image.fromarray(crop)
            tensors.append(self.bio_preprocess(pil))

        batch = torch.stack(tensors).to(self.device)
        with torch.no_grad():
            image_features = self.bio_model.encode_image(batch)
            image_features = F.normalize(image_features, dim=-1)
            # Cosine similarity -> logits -> temperature-scaled softmax
            logits = image_features @ self.text_features.T
            probs = F.softmax(logits / self.bioclip_temperature, dim=-1)
            probs = probs.cpu().numpy()          

        results = []
        for row in probs:
            top = int(np.argmax(row)) #return index/class with highest prob for the detection 
            results.append((self.to_common[self.labels[top]], float(row[top]))) #(class, prob)
        return results


    
    def _make_objects(self, results, frame: np.ndarray, timestamp:float, frame_id:int, with_ids=False):
        """Convert the output to a standardized class for processing"""
        if not results.boxes:
            return []

        boxes_xyxy = [tuple(b.xyxy[0].tolist()) for b in results.boxes] #get the box coordinates of all results
        bio_classes = self._bio_classification(frame, boxes_xyxy)

        detected_animals = []
        for box, bio_class in zip(results.boxes, bio_classes):
            label, bioclip_prob = bio_class
            detected = VideoDetection(
                label, #class
                bioclip_prob * float(box.conf), #confidence
                BoundingBox(*box.xyxy[0].tolist()), #bounding box for the animal, unpack points using *
                frame_id,
                timestamp,
                track_id= int(box.id) if with_ids and box.id is not None else None, #assign track number to it 
            )
            detected_animals.append(detected)
        return detected_animals
    
    def track(self, frame, timestamp:float, frame_id: int):
        """Extending the detection, to track animals across frames, calls sequentially as frames are ingested"""
        detected = self.model.track(
            frame,
            conf=self.confidence,
            imgsz=1280,              # MDv6 was trained at 1280
            classes=[0],             # animals only; drop 1 (person) and 2 (vehicle)
            persist=True,       # critical: keeps tracker state between calls
            tracker=str(TRACKER_CONFIG),  #Tracker, botsort uses features of the image to help track, useful if animals temporary leaves
            verbose=False,
        )[0]
        detected_obj = self._make_objects(detected, frame, timestamp, frame_id, with_ids=True)
        return self.smooter.smooth(detected_obj)

class AudioDetector:
    """Class for detecting audio events from the video, specifcally animal related"""
    def __init__(self, env: AudioEnvironment):
        self.labels = env.classes #set the relevant classes into the model so it knows what to predict

        #If time fix this later, would be better to predict each class individually rather than 
        #have them all compete in a softmax 
        self.pipeline = pipeline(
            "zero-shot-audio-classification",
            model="laion/larger_clap_general", #Use CLAP as PANN with classification flexibility
            device=_pick_device(),
        )
    def make_objects(self, results, timestamp:float, duration:float):
        """Convert the output to a standardized class for processing"""
        detected_sounds = []
        for detection in results:
            detected = AudioDetection(
                detection["label"],
                detection["score"],
                timestamp,
                duration
            )
            detected_sounds.append(detected)
        return detected_sounds

    def detect(self, audio_frame, timestamp:float, duration: float, top_k=2):
        """With a single audio segment, detect and classify the sound segment"""
        #for now im going to use the pieline with top k as a substitute for multiple detection, but its not great sub since the sigmoid stretches scores out
        #would be a lot better later if I have time to do the pipeline manually and then for each class check if it passes a threshold (multi label classificaiton)
        audio_detections = self.pipeline(
            audio_frame,
            candidate_labels=self.labels,
        )
        top_detections = audio_detections[:top_k] #grab the highest confidence score 
        return self.make_objects(top_detections,timestamp, duration )

