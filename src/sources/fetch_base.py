"""
The purpose of this is to provide an abstract media fetcher. 

The aim is to provide a URL such that the fetcher retrives the media and stores
it locally in data for processing for the ingestion layer to consume. 

This runs before the pipeline to produce data to be comsumed by the ingestor. 
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path



@dataclass
class MediaConfig:
    """this class will provide the config for the different medias I may use"""
    output_dir: Path = field(default_factory=lambda: Path("../data/raw_input")) #default store will be in raw inputs
    format: str = "bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]" #default for youtube
    quality: str | None = None
    filename_template: str = "%(title)s.%(ext)s" #default template name for stored video
    #check that the output directory is Path and the directory exists after initialization 
    def __post_init__(self):
        self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class MediaResults: 
    """Dataclass to store results of download"""
    title: str
    filepath: Path 
    url: str
    duration: float | None = None
    filesize: int | None = None 

class MediaFetcher(ABC):
    """Base class that is abstracted, implemented depending on websource (Youtube, twitch, etc...)"""
    def __init__(self):
        self.config = MediaConfig() #defaults to config for youtube

    @abstractmethod
    def download(self, url: str) -> MediaResults:
        ... #implement later

    @abstractmethod
    def get_metadata(self, url: str) -> dict:
        ... #implement later

    
