"""
Final pipeline that ingests a video, detects animals and sounds, fuses the signals, and analyses the results
"""

from src.ingest.ingester import IngestConfig, MediaStreamIngester
from src.detection.detector import VisualDetector, AudioDetector
import src.detection.environment as env
import src.detection.audio_environment as aenv
from src.fusion.temporal_fusion import FusionLayer
from src.analyse.analysis_layer import AnalysisLayer



def wildlife_monitor(video_path: str, environment: str) -> dict:

    config = IngestConfig(sample_fps=1.0)
    ingester = MediaStreamIngester(video_path, config)
    image_detector = VisualDetector(env.get(environment))
    audio_detector = AudioDetector(aenv.get(environment))

    #Go through and detect visual results 
    all_visual_results = []

    for frame, timestamp, i in ingester.iterate_frames():
        all_visual_results.extend(image_detector.track(frame, timestamp, i))

    #Go through and detect audio results 
    all_audio_results = []

    for waveform, timestamp in ingester.iterate_audio():
        all_audio_results.extend(audio_detector.detect(waveform, timestamp,config.audio_window))
        
    #fuse and print summaries
    fusion = FusionLayer(window_size=3.0)
    fused = fusion.fuse(all_visual_results, all_audio_results)

    #Analysis layer test
    analyser = AnalysisLayer(fused, environment)

    return {
        "animal_count": analyser.unique_animal_count(),
        "species": analyser.species_counts(),
        "dominant_sounds": analyser.dominant_sounds(),
        "events": [e.to_dict() for e in analyser.generate_all_events()],
    }