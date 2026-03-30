"""
The purpose of this class is to create visual and audio detectors
such that when a videostream is passed through the detectors find and store relevant information 
"""


import numpy as np
#from concurrent.futures import ThreadPoolExecutor
from .environment import Environment
from .detection_unit import VideoDetection, AudioDetection, BoundingBox
from ultralytics import YOLO
from pathlib import Path
from .util.tracking_smoother import TrackClassSmoother

#imports for audio
from transformers import pipeline
from .audio_environment import AudioEnvironment

TRACKER_CONFIG = Path(__file__).parent / "custom_botsort.yaml" #customization of the tracker paramters to see if i can opitmize animal detection.

class VisualDetector:
    """Class for detecting objects from the video, specifically animals"""

    def __init__(self, env: Environment, confidence=0.3):
        self.model = YOLO("yolov8x-worldv2.pt") 
        self.model.set_classes(env.classes) #set the relevant classes into the model so it knows what to predict
        self.confidence = confidence #sensitivity in prediciton, lower means more false positives
        self.smooter = TrackClassSmoother() #meant to help keep consistent labels within a frame range for the same tracked entity 
    
    def make_objects(self, results, timestamp:float, frame_id:int, with_ids=False):
        """Convert the output to a standardized class for processing"""
        detected_animals = []
        for box in results.boxes:
            detected = VideoDetection(
                results.names[int(box.cls)], #class
                float(box.conf), #confidence
                BoundingBox(*box.xyxy[0].tolist()), #bounding box for the animal, unpack points using *
                frame_id,
                timestamp,
                track_id= int(box.id) if with_ids and box.id is not None else None, #assign track number to it 
            )
            detected_animals.append(detected)
        return detected_animals

    
    def detect(self, frame, timestamp:float, frame_id: int):
        """With a single frame detect animals"""
        detected = self.model.predict(frame, conf=self.confidence, verbose=False)[0] #find all animals
        return self.make_objects(detected, timestamp, frame_id)
    
    def track(self, frame, timestamp:float, frame_id: int):
        """Extending the detection, to track animals across frames, calls sequentially as frames are ingested"""
        detected = self.model.track(
            frame,
            conf=self.confidence,
            persist=True,       # critical: keeps tracker state between calls
            tracker=str(TRACKER_CONFIG),  #Tracker, botsort uses features of the image to help track, useful if animals temporary leaves
            verbose=False,
        )[0]
        detected_obj = self.make_objects(detected, timestamp, frame_id, with_ids=True)
        return self.smooter.smooth(detected_obj)

class AudioDetector:
    """Class for detecting audio events from the video, specifcally animal related"""
    def __init__(self, env: AudioEnvironment, device="mps"):
        self.labels = env.classes #set the relevant classes into the model so it knows what to predict

        #If time fix this later, would be better to predict each class individually rather than 
        #have them all compete in a softmax 
        self.pipeline = pipeline(
            "zero-shot-audio-classification",
            model="laion/larger_clap_music_and_speech", #Use CLAP as PANN with classification flexibility
            device=device,
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

    def detect(self, audio_frame, timestamp:float, duration: float, sample_rate = 32000,top_k=2):
        """With a single audio segment, detect and classify the sound segment"""
        #for now im going to use the pieline with top k as a substitute for multiple detection, but its not great sub since the sigmoid stretches scores out
        #would be a lot better later if I have time to do the pipeline manually and then for each class check if it passes a threshold (multi label classificaiton)
        audio_detections = self.pipeline(
            audio_frame,
            candidate_labels=self.labels,
        )
        top_detections = audio_detections[:top_k] #grab the highest confidence score 
        return self.make_objects(top_detections,timestamp, duration )

