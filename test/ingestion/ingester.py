"""
Test to check if the Ingester functions work. 
More of a scratchpad to script test than automated validation tests. 
"""

from src.ingest.ingester import IngestConfig, MediaStreamIngester

#run from root folder
path = './data/raw_input/NamibiaCam： Baby Giraffe with family - 6⧸12⧸2021.mp4'

config = IngestConfig(sample_fps=1.0)
ingester = MediaStreamIngester(path, config)

all_frame_results = []

for chunk in ingester.iterate_frames():
    all_frame_results.append(chunk)


all_audio_results = []

for chunk in ingester.iterate_audio():
    all_audio_results.append(chunk)

print(all_audio_results[2:10])