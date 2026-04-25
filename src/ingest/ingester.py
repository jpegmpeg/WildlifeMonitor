"""
The Ingestor aims to decouple the meansof ingestion with the detection algorithm
I want to be able to change the ingestion logic later potentially for livestream 
so I dont want all that code to be done in the detection layer. 
The goal is to have an iterator that feeds frames or audio segments iteratively to be processedß
"""

from dataclasses import dataclass 
from typing import Iterator
import numpy as np
import av

@dataclass 
class IngestConfig:
    """"define ingestion configuration for the different streams"""
    #video streams 
    sample_fps: float = 5.0 #ingest at 5 FPS

    #audio
    audio_sample_rate: int = 32000 #can vary with audio model, but PANN expects 32kHz
    audio_window: float = 2 #5 second audio segment
    audio_step: float = 1 #step in seconds for next audio chunk (<audio_window ensures overlap)
    audio_format: str  = "s16"
    audio_max_range: float = 32768.0 #the max integer value for s16 format, this normalizes the audio chunks
    audio_layout: str = "mono"

#To add a new media stream (sensor), add a new iterator
class MediaStreamIngester:

    def __init__(self, path: str, config: IngestConfig = IngestConfig()):
        """define class and assign internally the general configs for media ingestion"""
        self.path = path
        self.config = config

        container = av.open(path)
        self.og_fps = float(container.streams.video[0].average_rate) #I want to make sure its a manageable framerate, og might be too high
        container.close()
    
    def iterate_frames(self) -> Iterator[tuple[np.ndarray, float, int]]:
        """Iterator over the video and yields (frame, timestamp, frame_id) at the desired fps"""

        container = av.open(self.path) #enter stream processor 
        stream = container.streams.video[0]
        interval = max(1, int(round(self.og_fps / self.config.sample_fps))) #Takes either every frame, or at an interval base don config fps, say its originally at 60fps and we want to sample 5fps, the we grab every 12th frame. 

        for i, frame in enumerate(container.decode(stream)):
            if i % interval != 0: #check if we want to skip as we cycle through frames 
                continue
            yield ( #encounter frame at the right interval sepcified through fps, give it to the consumer
                frame.to_ndarray(format="bgr24"), #use bgr24 since that is what YOLO expects 
                float(frame.pts * stream.time_base), #timestamp
                i,
            )

        container.close()

    def iterate_audio(self) -> Iterator[tuple[np.ndarray, float]]:
        """Iterator over the audio segments and yields (waveform, timestamp) at the desired overlap"""

        container = av.open(self.path)
        resampler = av.AudioResampler(format=self.config.audio_format, layout=self.config.audio_layout, rate=self.config.audio_sample_rate)

        # Decode full audio
        samples = []

        #go through all the audio frames, resample them and then flatten and normalize
        for frame in container.decode(audio=0):
            frame = resampler.resample(frame)[0] #grab the first frame in the sample
            samples.append(frame.to_ndarray().flatten().astype(np.float32) / self.config.audio_max_range)
        container.close()

        audio = np.concatenate(samples)       

        #use a window to get overlap between values to enahnce detection 
        window = int(self.config.audio_window * self.config.audio_sample_rate)
        step = int(self.config.audio_step * self.config.audio_sample_rate)
        offset = 0

        #continuously go through the audio file in chunks as big as the window and offset the next unit given to start at a level of overlap within the previous
        while offset <= len(audio):
            chunk = audio[offset : offset + window]
            if len(chunk) < window: #case where the audio file time isnt divisible by the window size, pad 0s
                chunk = np.pad(chunk, (0, window - len(chunk)), mode='constant')
            yield chunk, offset / self.config.audio_sample_rate # second is estimate of timestamp
            offset += step