"""
Detection pipeline to paralellize visual and audio processing.
Threads since most of process is in pytorch and pyav which doesnt run through GIL
"""

import queue
import threading
from dataclasses import dataclass
from typing import Any
from src.ingest.ingester import MediaStreamIngester
from src.detection.detector import VisualDetector, AudioDetector

#a sentinel object used to signal "no more items on this queue".
#using a unique object instead of None means None-valued items could still
#legitimately be queued if needed later
_SHUTDOWN = object()

@dataclass
class FrameItem:
    frame: Any
    timestamp: float
    frame_id: int


@dataclass
class AudioItem:
    waveform: Any
    timestamp: float


def run_parallel_detection(ingester: MediaStreamIngester, image_detector: VisualDetector, audio_detector: AudioDetector, audio_window: float) -> tuple[list, list]:
    """
    Returns (visual_results, audio_results). Raises the first exception
    encountered in any worker thread.
    """

    #bounded queues for backpressure. 
    frame_queue: queue.Queue = queue.Queue(maxsize=8)
    audio_queue: queue.Queue = queue.Queue(maxsize=16)

    #errors from any thread get pushed here so the main thread can raise them.
    error_queue: queue.Queue = queue.Queue()

    visual_results: list = []
    audio_results: list = []

    seen_tracks = set()

    #stop flag lets consumers exit early if a producer errors out.
    stop_event = threading.Event()

    ################ Producers ##################
    def video_producer():
        """Producer for video frames, push the frames to queue"""
        try:
            for frame, timestamp, frame_id in ingester.iterate_frames():
                #yield from the ingester
                if stop_event.is_set(): #if there is an error in the producer end
                    return
                #when there is no error from producer
                while not stop_event.is_set():
                    try:
                        #put the frame into queue to be consumed later
                        frame_queue.put(FrameItem(frame, timestamp, frame_id), timeout=0.5)
                        break
                    except queue.Full:
                        continue #when the queue is full  get the next batch 
        except Exception as e:
            error_queue.put(("video_producer", e))
            stop_event.set()
        finally:
            frame_queue.put(_SHUTDOWN) #end of queue

    def audio_producer():
        """Producer for audio frames, push to audio queue"""
        try:
            for waveform, timestamp in ingester.iterate_audio():
                #yiled an audiochunk
                if stop_event.is_set():
                    return #if error break
                while not stop_event.is_set():
                    try:
                        #put audio event into queue
                        audio_queue.put(AudioItem(waveform, timestamp), timeout=0.5)
                        break
                    except queue.Full:
                        continue
        except Exception as e:
            error_queue.put(("audio_producer", e))
            stop_event.set()
        finally:
            audio_queue.put(_SHUTDOWN) #end of queue


    ################ Consumers ##################
    def video_consumer():
        """Detector for video"""
        try:
            while True:
                #get next item in queue
                item = frame_queue.get()
                if item is _SHUTDOWN: #if reach the end (nothing more is being added to queue)
                    return
                detections = image_detector.track(item.frame, item.timestamp, item.frame_id)

                #since I havent implemented this for livestream, but a requirement is an Alert, I will implement one here
                #it will print in the consol as its ingesting the video frames if a new animal has been detected 
                for detected in detections:
                    if detected.track_id is not None and detected.track_id not in seen_tracks:
                        seen_tracks.add(detected.track_id)
                        alert = f"[ALERT] New {detected.label} detected at {item.timestamp:.1f}s"
                        print(alert)
                visual_results.extend(detections)
        except Exception as e:
            #error queue add if issue, stop if an error is encountered
            error_queue.put(("video_consumer", e))
            stop_event.set()

    def audio_consumer():
        """Detector for audio"""
        try:
            while True:
                #get the next audio in queue
                item = audio_queue.get()
                if item is _SHUTDOWN: #if reach the end (nothing more is being added to queue)
                    return
                detections = audio_detector.detect(item.waveform, item.timestamp, audio_window)
                audio_results.extend(detections)
        except Exception as e:
            error_queue.put(("audio_consumer", e))
            stop_event.set()

    #for each of these producers and consumers, make a thread (since they all use C under the hood and avoid GIL)
    threads = [
        threading.Thread(target=video_producer, name="video_producer"),
        threading.Thread(target=video_consumer, name="video_consumer"),
        threading.Thread(target=audio_producer, name="audio_producer"),
        threading.Thread(target=audio_consumer, name="audio_consumer"),
    ]
    #start threads and join them
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    #surface the first error if any
    if not error_queue.empty():
        origin, exc = error_queue.get()
        raise RuntimeError(f"Worker {origin} failed") from exc

    return visual_results, audio_results