"""
Obejct to store distinct events so that users can more easily consume post-fusion event processing
"""

from dataclasses import dataclass, field

@dataclass
class Event:
    event_type: str           #generate by the analysis function to keep continuity 
    timestamp: float          
    duration: float           
    description: str          
    confidence: float = 0.0   #aggregate confidence for the event, this should combine the confidence scores for the deteciton
    labels: list[str] = field(default_factory=list ) #relevant visual/audio labels involved
    
    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "duration": self.duration,
            "description": self.description,
            "confidence": self.confidence,
            "labels": self.labels,
        }


