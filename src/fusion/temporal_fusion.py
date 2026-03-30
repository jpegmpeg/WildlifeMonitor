"""
I want to temporally align the features extracted from the visual and audio detectors 
By co-locating the events from the two sensors, I can more easily perform operations on the fused object to extrract information 
"""

from dataclasses import dataclass, field
from src.detection.detection_unit import VideoDetection, AudioDetection

@dataclass
class FusedDetection:
    """fused class that co-locates the audio and video detections in a time window"""
    window_start: float 
    window_end: float
    visual: list[VideoDetection] = field(default_factory=list)
    audio: list[AudioDetection] = field(default_factory=list)

    @property
    def has_visual(self) -> bool: #is there a visual detection in the time window?
        return len(self.visual) > 0
 
    @property
    def has_audio(self) -> bool: #is there an audio detection in the time window?
        return len(self.audio) > 0
 
    @property
    def has_both(self) -> bool: #is there a visual and audio detection in the time window, thereby making it multimodal?
        return self.has_visual and self.has_audio
 
    @property
    def visual_labels(self) -> list[str]:  #what were the classes detected by the visual model
        return list({d.label for d in self.visual})
 
    @property
    def audio_labels(self) -> list[str]: #what were the classes detected by the audio model
        return list({d.label for d in self.audio})
    
    def summary(self) -> dict: #easier to see for testing
        return {
            "time": f"{self.window_start:.1f}s - {self.window_end:.1f}s",
            "visual": self.visual_labels,
            "audio": self.audio_labels,
            "multimodal": self.has_both,
        }
    
class FusionLayer:
    """
    I want to store/co-localize events from the vision and audio detector that happen wihin a timewindow.
    If a timestamp for the detection happens in the window it is assinged to that window. 
    Since audio events already exist in windows, to reduce redundancy, I will have the middle of the window act as a timestamp
    I will see later if i have time about trying another way to get sharper precision. 
    """
    def __init__(self, window_size: float = 2.0):
        self.window_size = window_size

    def get_bin(self, timestamp:float) -> int:
        """"treating windows as a bin, so assign a bin to a timestamp"""
        return int(timestamp // self.window_size) #floor divide gives bin
    
    def audio_center_bin(self, detection: AudioDetection) -> int:
        """i want the audio window center to be the timestamp i assing to a bin to avoid duplicates"""
        center_time = detection.timestamp + detection.duration / 2
        return self.get_bin(center_time)
    def fuse(self,visual_detections: list[VideoDetection],audio_detections: list[AudioDetection]) -> list[FusedDetection]:
        """co-locate all the videodetection and audiodetection objects based on timestamps and return a fused object"""

        bins: dict[int, FusedDetection] = {}

        #Checks if the bin already has a FusedDetection object in it, and if it doesnt, then it creates one 
        def check_bin(b: int) -> FusedDetection:
            if b not in bins:
                bins[b] = FusedDetection( #make the window cover the bin's range based on bin size
                    window_start=b * self.window_size,
                    window_end=(b + 1) * self.window_size,
                )
            return bins[b] #this is a fusion detection object
        
        #assgn detected visual objects to its respective bin
        for detection in visual_detections:
            b = self.get_bin(detection.timestamp)
            check_bin(b).visual.append(detection)

        #assgn detected audio objects to itsrespective bin
        for detection in audio_detections:
            b = self.audio_center_bin(detection)
            check_bin(b).audio.append(detection)


        return sorted(bins.values(), key=lambda f: f.window_start) #sort the bins based on timeline of window start