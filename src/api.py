"""
API to manage interaction between backend logic and front end. 
Using FastAPI to quickly get an API going for a forntend 
"""

from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from src.clean import clear_directory

from src.wildlife_monitor import wildlife_monitor
from src.sources.youtube import  YouTubeFetcher


BASE_DIR = Path(__file__).parent.parent #this brings you to the root folder
print(BASE_DIR)
DATA_DIR = BASE_DIR / "data" 
print(DATA_DIR)
FRAMES_DIR = DATA_DIR/ "output" / "frames"
VIDEO_DIR = DATA_DIR / "raw_input"

app = FastAPI()

app.add_middleware(
    CORSMiddleware, #since on diff ports
    allow_origins=["http://localhost:3000"], #well my react will be
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/frames", StaticFiles(directory=str(FRAMES_DIR)), name="frames") #where snapshots will be stored 

#have the youtube downloader be its own so the video can load and analyse it after its loaded
@app.post("/download")
async def download(url: str = Form(...)):
    """Download the video."""
    clear_directory(VIDEO_DIR)
    clear_directory(FRAMES_DIR)
    yt = YouTubeFetcher()
    video_info = yt.download(url) #downloads the video from the url and stores it in the 
    video_path = video_info.filepath
    filename = Path(video_path).name
    return {"video_url": f"/video/{filename}", "filename": filename} 
    

@app.post("/analyze") #main analysis pipeline for the event detection 
async def analyze(filename: str = Form(...), environment: str = Form("FOREST")):
    """ingest the video and runs through the whole event analysis pipeline"""
    #If i spent more time i could make this into fragmented sends with buffer to analyse livestreams, for now just videos
    video_path = str(VIDEO_DIR / filename)
    results = wildlife_monitor(video_path, environment)
    results["video_url"] = f"/video/{filename}"

    # add frame URLs to each event so i can display it in the timeline
    for i, event in enumerate(results["events"]):
        event["frame_url"] = f"/frames/{i:04d}_{event['event_type']}_{event['timestamp']:.1f}s.png" #naming convention to match snapshot image saving

    return results

@app.get("/video/{filename}") #grabbing the video from 
async def serve_video(filename: str):
    video_path = VIDEO_DIR / filename
    if not video_path.exists():
        return {"error": "Video not found"}
    return FileResponse(str(video_path), media_type="video/mp4")

#Check the server is good
@app.get("/health")
async def health():
    return {"status": "ok"}
