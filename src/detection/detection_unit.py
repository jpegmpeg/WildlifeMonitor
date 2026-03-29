"""
These are the detectable units of the model. These classes help define what will extracted
from the streams that will then later be processsed. The goal of having detection class is that this
provides the fundamental information to work with so I dont have to rely on the whole stream which 
would be too large to keep in memory 
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

class StreamType(Enum):
    """media type for the stream"""
    VISUAL = auto() #automatically assing incrementor within it incase other streams are added later 
    AUDIO = auto()

@dataclass 
class BoundingBox:
    """For visual detection a bounding box is necessary to track visual space is consumed by the object"""
    x1: float #topleft
    y1: float #topleft
    x2: float #bottomright
    y2: float #bottomright

    @property
    def width(self) -> float:
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        return self.y2 - self.y1

    @property
    def area(self) -> float: 
        return self.width * self.height
    
    @property
    def center(self) -> tuple[float, float]:
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)
    

    
@dataclass 
class VideoDetection:
    """Relevant video features extracted by the CNN"""
    label: str
    confidence: float
    box : BoundingBox
    frame_id: int
    timestamp: float
    source = StreamType.VISUAL.value
    track_id: int | None = None

@dataclass 
class AudioDetection:
    """Relevant audio features detected by the ANN"""
    label: str
    confidence: str
    timestamp: str
    duration: float
    source = StreamType.AUDIO.value



