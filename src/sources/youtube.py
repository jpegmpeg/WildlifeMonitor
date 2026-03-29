from fetch_base import MediaFetcher, MediaResults
from urllib.parse import urlparse
import yt_dlp
from pathlib import Path

class YouTubeFetcher(MediaFetcher):
    """YouTube-specific implementation"""

    VALID_HOSTS = {"youtube.com", "youtu.be", "www.youtube.com"} #to ensure a youtube url is passed

    def __init__(self):
        super().__init__() # sets self.config = MediaConfig() (could be useufl to change later on for other types)

    def validate_url(self, url: str) -> bool:
        """Ensure the url passed is youtube"""
        return urlparse(url).hostname in self.VALID_HOSTS 
    
    def get_metadata(self, url: str) -> dict:
        """retrieve metadata about the video"""
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            return ydl.extract_info(url, download=False) 
        
    def download(self, url: str) -> MediaResults:
        """download the youtube video and save it in the output_dir"""
        if not self.validate_url(url):
            raise ValueError(f"Not a valid YouTube URL: {url}")
        
        #set options to be used by the youtube downloader for format and filepath
        options = {
            "format": self.config.format, 
            "outtmpl": str(self.config.output_dir / self.config.filename_template), #filename template 
            "quiet": False,
            "no_warnings": False,
            "merge_output_format": "mp4",
        }

        #download the youtube video and save the metadata 
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = Path(ydl.prepare_filename(info))

            return MediaResults(
                title=info.get("title", "none"),
                filepath=filepath,
                url=url,
                duration=info.get("duration"),
                filesize=info.get("filesize"),
            )