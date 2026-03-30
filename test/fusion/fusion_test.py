"""
Test to check if the Detector work. 
More of a scratchpad to script test than automated validation tests. 
"""

from src.ingest.ingester import IngestConfig, MediaStreamIngester
from src.detection.detector import VisualDetector, AudioDetector
import src.detection.environment as env
import src.detection.audio_environment as aenv
from src.fusion.temporal_fusion import FusionLayer
from tabulate import tabulate
from src.analyse.analysis_layer import AnalysisLayer

#run from root folder, this is a test video
path = './data/raw_input/NamibiaCam： Baby Giraffe with family - 6⧸12⧸2021.mp4'

config = IngestConfig(sample_fps=1.0)
ingester = MediaStreamIngester(path, config)
image_detector = VisualDetector(env.SAVANNA)
audio_detector = AudioDetector(aenv.SAVANNA)


#Go through and detect visual results 
all_visual_results = []

for frame, timestamp, i in ingester.iterate_frames():
    detected_animals = image_detector.track(frame, timestamp, i)
    all_visual_results.append(detected_animals)


#Go through and detect audio results 
all_audio_results = []

for waveform, timestamp in ingester.iterate_audio():
    detected_sounds = audio_detector.detect(waveform, timestamp,config.audio_window)
    all_audio_results.append(detected_sounds)

all_visual = [detection for frame_detections in all_visual_results for detection in frame_detections]
all_audio = [detection for audio_detection in all_audio_results for detection in audio_detection]

#fuse and print summaries
fusion = FusionLayer(window_size=3.0)
fused = fusion.fuse(all_visual, all_audio)

#Analysis layer test
analyse = AnalysisLayer(fused, "SAVANNA")
analyse.print_event_log()