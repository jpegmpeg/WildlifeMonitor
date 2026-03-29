"""
Test to check if the Detector work. 
More of a scratchpad to script test than automated validation tests. 
"""

from src.ingest.ingester import IngestConfig, MediaStreamIngester
from src.detection.detector import AudioDetector
from src.detection.detection_unit import AudioDetection
import src.detection.environment as env
import src.detection.audio_environment as aenv
from tabulate import tabulate

#run from root folder
path = './data/raw_input/NamibiaCam： Baby Giraffe with family - 6⧸12⧸2021.mp4'

config = IngestConfig(sample_fps=1.0)
ingester = MediaStreamIngester(path, config)
audio_detector = AudioDetector(aenv.SAVANNA)

all_detection_results = []

for waveform, timestamp in ingester.iterate_audio():
    detected_sounds = audio_detector.detect(waveform, timestamp,config.audio_window)
    all_detection_results.append(detected_sounds)

print(all_detection_results[2:6])
#def show_detections(frames: list[list[VideoDetection]]):
#    rows = []
#    for frame_detect in frames:
#        for det in frame_detect:
#            rows.append([
#                det.frame_id,
#                f"{det.timestamp:.2f}s",
#                det.track_id,
#                det.label,
#                f"{det.confidence:.0%}",
#                f"{det.box.width:.0f}x{det.box.height:.0f}",
#                f"{det.box.area:.0f}",
#            ])
#
#    print(tabulate(
#        rows,
#        headers=["Frame", "Time", "Track", "Label", "Conf", "Size", "Area"],
#        tablefmt="simple",
#    ))

#show_detections(all_detection_results)