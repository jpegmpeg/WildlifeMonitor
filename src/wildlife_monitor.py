"""
Final pipeline that ingests a video, detects animals and sounds, fuses the signals, and analyses the results
"""

from src.ingest.ingester import IngestConfig, MediaStreamIngester
from src.detection.detector import VisualDetector, AudioDetector, ModelConfig
from src.detection.parallel_detection import run_parallel_detection
import src.detection.environment as env
import src.detection.audio_environment as aenv
from src.fusion.temporal_fusion import FusionLayer
from src.analyse.analysis_layer import AnalysisLayer
from src.analyse.snapshot import snapshot_event_frames
import time



def wildlife_monitor(video_path: str, environment: str) -> dict:

    config = IngestConfig(sample_fps=1.0)
    ingester = MediaStreamIngester(video_path, config)
    model_config = ModelConfig()
    image_detector = VisualDetector(env.get(environment),model_config)
    audio_detector = AudioDetector(aenv.get(environment))

    #Go through and detect visual results 
    all_visual_results = []
    all_audio_results = []

    print("------------------ Ingestion Begins --------------------------")
    start = time.perf_counter()
    all_visual_results, all_audio_results = run_parallel_detection(
        ingester, image_detector, audio_detector, config.audio_window
    )
    print(f"[TIMING] Detection Complete: {time.perf_counter() - start:.2f}s")
    print("------------------  Ingestion Done  --------------------------")

    #fuse and print summaries
    fusion = FusionLayer(window_size=3.0)
    fused = fusion.fuse(all_visual_results, all_audio_results)

    #Analysis layer test
    analyser = AnalysisLayer(fused, environment)
    all_events = analyser.generate_all_events()
    wildlife_found =  {
        "animal_count": analyser.unique_animal_count(),
        "species": analyser.species_counts(),
        "dominant_sounds": analyser.dominant_sounds(),
        "events": [e.to_dict() for e in all_events],
    }

    snapshot_event_frames(video_path, all_events)
    
    return wildlife_found
