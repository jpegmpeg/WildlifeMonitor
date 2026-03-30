# Wildlife Monitor

Wildlife monitor provides a multimodal feature detection, classification, and tracking of animals that appear in videos from live animal and nature camera setups. The application logs, alerts, and creates a timeline of key events in the video segment based on the animal's activity. By receiving a link to a youtube video of wildlife cameras in any envionrment (whether it be a forest, he savanna desert, or the arctic), the application will attempt to monitor the local wildlife.

Biomes include: forests, wetlands, the Savanna, the arctic, ubran settings, and mountain ranges. 

## Demo

https://www.loom.com/share/ff179a22305440ccbb3b902cae75be66

## Setup & Installation
 
### Prerequisites
 
- Python 3.12+
- Node.js 22+
- FFmpeg
 
### Quick Setup
 
```bash
git clone <repo-url>
cd Wildlife_monitor
bash setup.sh
```

## Usage
 
**1. Start the backend:**
 
```bash
source env/bin/activate
uvicorn src.api:app --reload --port 8000
```
 
**2. Start the frontend:**
 
```bash
cd frontend
npm run dev
```
 
**3. Open `http://localhost:3000` in your browser.**
 
**4.** Paste a YouTube URL, select an environment, click **Download**, then click **Analyze**.
 
The downloaded videos appears on the right and the results are populated below and include:
summary statistic showing animal count, species, and dominant sounds, followed by an event timeline with frame snapshots at the start of those events.

## Project Structure
 
```
Wildlife_monitor/
├── src/
│   ├── api.py                    # FastAPI endpoints
│   ├── wildlife_monitor.py       # Main pipeline orchestration
|   ├── clean.py                  # Cleans folders with data
│   ├── ingest/
│   │   └── ingester.py           # Media stream ingestion (video + audio iterators)
│   ├── detection/
│   │   ├── detector.py           # Visual (YOLO-World) and Audio (CLAP) detectors
│   │   ├── detection_unit.py     # VideoDetection, AudioDetection dataclasses
│   │   ├── environment.py        # Visual environment definitions
│   │   └── audio_environment.py  # Audio environment definitions + ambient labels
│   ├── fusion/
│   │   └── temporal_fusion.py    # Time-window binning of detections for fusion
│   ├── analyse/
│   │   ├── analysis_layer.py     # Event detection and scene analysis
│   │   └── snapshot.py           # Frame extraction for events
|   |   └── event.py              # Event class
│   └── sources/
│       └── youtube.py            # YouTube video downloader
|       └── download.py           # Command line run for Youtube download (used only during development)
|       └── fetch_base.py         # Abstract Base class for media fetchers (only implemented for Youtube in the end)
├── frontend/                     # Next.js frontend
│   └── src/app/page.tsx          # Main UI
├── data/
│   ├── raw_input/                # Downloaded youtube video
│   └── output/
│       └── frames/               # Event frame snapshots 
├── test/...                      # Scratchpad to run test during development 
├── setup.sh
└── pyproject.toml
```

## Architecture

The application is broken into a 5-layer pipeline, such that each layer's output is standardized by class definitions for decoupling
```
YouTube URL ---> Ingestion ---> Detection ---> Fusion ---> Analysis ---> API +Frontend
                • Video       • YOLO-World      Time        Events        FastAPI         
                  frames        (visual)        window      Species       Next.js   
                • Audio       • CLAP            binning     Counts        
                  chunks        (audio)                     Alerts                
```

At each stage I ensured that communication between the layers is done through standardized classes (e.g.`VideoDetection`, `AudioDetection`, `FusedDetection`, `Event` ) so that I could change individual layers wihtout having to refactor other layers dependent on it. 

## Design Decisions

### Media Fetching Generalization

I originally abstracted `MediaFetcher` to be able to implement the class for different media platforms that may have their own video download configuration (e.g. Twitch). While I ended up only implementing Youtube via `YouTubeFetcher`, other media platforms can easily be incorporated into the pipeline through implementation and insertion into the exisiting framework. 
 
### Iterator-Based Ingestion

I used `MediaStreamIngester` as a means of providing an iterable generator to yield video frames and audio chunks sequentially. This decouples the media source from the detection layer's logic, the media platform source is irrelevant, it just provides the basic units needed for detection. While I did not get to livestream processing, this would help more easily implement a digestion of the units with a buffer.

Furthermore, I allowed for configurable FPS to avoid over procesing frames from potentially high frame-rate sources. Audio is decoded and resampled to 32kHz ,to be easily processed by the audio classifier, and yielded audio chunks in overlapping 5-second windows with an adjustable step to capture potentially truncated audio signatures at window boundaries. 
 
### Zero-Shot Visual Detection with Tracking and Audio Classification with CLAP

At the beginning of development I decided I wanted to have the flexiblity to detect wildlife in multiple different environments. Since wildlife is often varied, even within the same environmnet, this can pose challenges for CNN that are well-trained on very specific animals. As such, I wanted models with class flexibility, since I decided it would be a cleaner implementation than training myself. 

The visual detector uses YOLO-World (`yolov8x-worldv2`), an open-vocabulary model that detects objects based on the class labels provided to it, rather than a fixed set of labels it was trained on. This means as environments change or specific animals become of interest, it becomes a simple matter of just updating the environment class list without retraining. I also made use of BotSort in an attempt to leverage visual appearance to track and maintain persistent animal IDs. Futhermore, I added a custom class `TrackClassSmoother` to stabilizes label assignments across frames for the same tracked entity, reducing label flickering.

Teh audio detector uses CLAP (`laion/larger_clap_music_and_speech`), a contrastive audio-text model that matches audio embeddings against text label embeddings. Much like YOLO-World, it is open-vocabulary and new sounds can be added to the audio environments class list. An important decision I made was rewriting all audio labels to describe acoustic qualities rather than species or behavior. CLAP matches sounds against text embeddings, so acoustic descriptors are far more effective. Futhermore, adding species or intent behind the classlabel can be misleading to what is actually being detected, since some sounds have very similar spectral properties, without concept of the entity or emotions. 

### Custom environments 

Detection targets are organized by environment/biome. Each environment defines two things:
 
- **Visual environment** (`Environment`): Species for YOLO-World (e.g., "giraffe", "zebra" for savanna)
- **Audio environment** (`AudioEnvironment`): Acoustically-descriptive sound classes split into biological and ambient categories

Since wildlife camera footage can contain a lot of quiet periods, I created a separate class of ambient sounds, making it easy to update what counts as "background noise" across the entire system.
 

### Temporal Fusion

All the visual and audio detections are binned into fixed-length time windows (default 3 seconds) to create `FusedDetection` objects that contain all co-occurring events. I made it such that the audio detections are assigned to the bin containing their midpoint rather than being spread across all overlapping bins, which avoids duplication in downstream counting while still achieving alignment with visual events. The fusion layer is a pure data container, I left the inference to another layer to decouple the task of "how to fuse" and "what to analyse". 

### Analysis Layer

The `AnalysisLayer` consumes fused detections and produces `Event` objects representing meaningful occurrences. I wanted to maintain flexibility of this class so that adding a new analysis was as easy as writing a new function that returns a  list of `Event` objects. I decided to have three levels of analysis, visual only (animal entering and exiting, specie identification and count), audio only (quiet periods, peak loud periods), and combined (offscreen animal detection, corroborated visual and audio detection). Futhermore, confidence is assigned to the events as aggregated, often by averaging, of the confidence of the individual detections. 

For certain audio events, confidence-based thresholding is used throughout rather than simple presence checks. For example, quiet periods are identified when the ratio of ambient-to-total confidence exceeds a threshold, and loud events require non-ambient confidence to dominate. However, because confidence scores for the labels are the result fo softmaxing of scores, this thresholding can sometimes be misleading. One important factor that I would implement if I had more time would be to circumvent the transformer pipeline and implement multi-label classification using a sigmoid per label. Multiple sounds do genuinely co-occur in the same window, and having a multi-label classification would be a better approach than using confidence scores in a single-label framework that the current audio detector softmaxes for. 

### Two-Endpoint API
 
The download and analysis endpoints are separate so the user can start playing the video immediately after download while analysis runs in the background. This avoids the user staring at a blank screen during the full processing pipeline.

