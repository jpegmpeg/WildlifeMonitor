"""
Take the fused objects, and perform multi-sense and uni-sense analyses
Distinct layer to decouple from fusion process itself.
"""

from dataclasses import dataclass
from src.fusion.temporal_fusion import FusedDetection
import src.detection.audio_environment as aenv
from .event import Event

@dataclass
class TrackLog:
    """Specific tracked animal's presence in the scene"""
    track_id: int
    label: str
    first_seen: float  #timestamp in seconds
    last_seen: float
    window_count: int  #how many windows it appeared in



class AnalysisLayer:
    """Analysis Inference layer consumes fused object streams and performs various event detections"""

    def __init__(self, fused: list[FusedDetection], audio_environment: str):
        self.fused = fused
        self.ambient_labels = aenv.get_ambient(audio_environment)

    #VISION ONLY EVENT DETECTION/DISCRIPTS

    def unique_animal_count(self) -> int:
        """Assess unique animal count for the tracked animals across the scene"""
        track_ids = set() # keep track of unique tracking ids
        for f in self.fused: 
            for detected in f.visual: #look at all the visual detected events 
                if detected.track_id is not None:
                    track_ids.add(detected.track_id) #add the unique animal to the set
        return len(track_ids) #see how many unique animals there were

    def species_counts(self) -> dict[str, int]:
        """Assess how many unique species are in the camera's view and their count"""

        species: dict[str, set[int]] = {} #make the counter a set to keep track of unique ids for that specie then can jsut get len
        for f in self.fused: 
            for detected in f.visual: #go through each detected animal in the visual scope
                if detected.track_id is not None:
                    species.setdefault(detected.label, set()).add(detected.track_id) #set default in case it inst in the dict yet
        return {label: len(ids) for label, ids in species.items()}       #this then because a matter of getting distinct ids for specie

    def track_summaries(self) -> list[TrackLog]:
        """Get a timeline for when animals enter and exit to create specific events"""

        #Currently it assumes once video is done tracking ends, not compatible yet wiht live streaming
        #Will generalize alter if time permitted 
        tracks: dict[int, dict] = {} #
        for f in self.fused:
            for detected in f.visual: #go through all the visual detections 
                if detected.track_id is None:
                    continue
                if detected.track_id not in tracks: #first time tracking this entity
                    #Note this is the first time this animal enters frame, store in track
                    tracks[detected.track_id] = {
                        "label": detected.label,
                        "first_seen": detected.timestamp,
                        "last_seen": detected.timestamp,
                        "windows": set(),
                    }
                #get the track for the tracking id
                t = tracks[detected.track_id]
                #update the track  based on the detected animal currently considered 
                t["first_seen"] = min(t["first_seen"], detected.timestamp) #min first time seeing animal tracked? 
                t["last_seen"] = max(t["last_seen"], detected.timestamp) #max latest time seing animal tracked
                t["windows"].add(f.window_start) #accumulate window
        return [
            TrackLog(track_id, track["label"], track["first_seen"], track["last_seen"], len(track["windows"]))
            for track_id, track in tracks.items() #cycle through all the tracks accumulated and make a tracklog
        ]

    def entries_and_exits(self) -> list[Event]:
        """Log entries and exists as events for later user consumption"""
        events = []
        for s in self.track_summaries(): #go through all the tracking summaries and create a log of enters and exits
            events.append(Event(
                "ANIMAL_ENTERED",
                timestamp=s.first_seen,
                duration=0,
                description=f"{s.label} entered the scene", #use the animal label to track species
                labels=[s.label],
            ))
            events.append(Event(
                "ANIMAL_EXITED",
                timestamp=s.last_seen,
                duration=0,
                description=f"{s.label} exited the scene", 
                labels=[s.label],
            ))
        return events


    #AUDIO ONLY EVENT DETECTION/DISCRIPTS 
    def dominant_sounds(self, top_k: int = 3) -> list[tuple[str, float]]:
        """determine the dominat sound that is pervasive against the whole segment being consumed"""

        #I want to weight the different sounds based off their confidence scores to make repitition AND accuracy relevant
        scores: dict[str, float] = {}
        for f in self.fused: 
            for detected in f.audio: #got through each audio fusion object
                scores[detected.label] = scores.get(detected.label, 0.0) + detected.confidence #use the confidence as the 
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True) #sort from highest score to lowest
        return ranked[:top_k]
    
    def non_ambient_thresholding(self, f: FusedDetection) -> float | None:
        """Below i will use ratio of confidence scores to ambient to help threshold certain loud events (better appraoch would be multilalbel audio classes but i will get to it if I have time)"""
        if not f.audio:#If no audio in the fused object skip
            return None

        total_conf = sum(detected.confidence for detected in f.audio) #use the confidence score as proxy for now
        if total_conf == 0:#avoid division by 0
            return None
        
        #get confidence score of non ambient confidence
        non_ambient_conf = sum(detected.confidence for detected in f.audio if detected.label not in self.ambient_labels)

        return non_ambient_conf / total_conf
    
    def quiet_periods(self, ambient_ratio: float = 0.5) -> list[Event]:
        """determine the quiet periods within the segment"""
        quiet_windows = [] #track periods of quietness 
        for f in self.fused:
            if not f.audio: #check if there is any audio event, if not then append (assumed quiet)
                quiet_windows.append(f)
                continue

            total_conf = sum(detected.confidence for detected in f.audio) #total confidence 
            if total_conf == 0: #check to avoid division by 0
                continue
            #get overall confidence in ambient scores
            ambient_conf = sum(detected.confidence for detected in f.audio if detected.label in self.ambient_labels)
            if ambient_conf / total_conf >= ambient_ratio:
                quiet_windows.append(f) #see if it passes ambient threshold
            
        #now that we have all the fused objects that are quiet, lets get the quiet periods    
        if not quiet_windows: #if there were no quiet periods just make it empty 
            return []
        
        #set up tracking for extended quiet periods 
        ranges = []
        start = quiet_windows[0].window_start
        end = quiet_windows[0].window_end    
        ambient_scores = []  # track confidence across the range

        #go through each quiet fused object 
        for w in quiet_windows[1:]:
            if w.window_start <= end:  # consecutive windows of fused objected
                end = w.window_end
                #tack on the scores for consecutive windows
                ambient_scores.extend(detect.confidence for detect in w.audio if detect.label in self.ambient_labels)
            else:
                ranges.append((start, end, ambient_scores)) #store the quiet period because its be disrupted
                start = w.window_start #start a new window
                end = w.window_end
                #reset ambient score store
                ambient_scores = [detected.confidence for detected in w.audio if detected.label in self.ambient_labels]

        ranges.append((start, end, ambient_scores)) #get the last quiet period and append
        return [
            Event(
                event_type="QUIET_PERIOD",
                timestamp=s,
                duration=e - s,
                description=f"Quiet period from {s:.1f}s to {e:.1f}s", 
                confidence=sum(scores) / len(scores) if scores else 0.0, #make the confidence the average confidence score
                labels=[],
            )
            for s, e, scores in ranges
        ]

    def peak_loud_windows(self, top_k: int = 5, threshold: float = 0.6) -> list[Event]:
        """Find the top fusion object windows where there has been a period of meaningful noise"""
        scored = []
        for f in self.fused:
            if not f.audio: #If no audio in the fused object skip
                continue
            ratio = self.non_ambient_thresholding(f)
            if ratio >= threshold: #check if confidence of relative non ambient is above threshold
                #get non ambient labels in audio
                non_ambient = [detected for detected in f.audio if detected.label not in self.ambient_labels]
                non_ambient_conf = sum(detected.confidence for detected in non_ambient) #sum the scores
                scored.append((f, non_ambient_conf, non_ambient)) 

        scored.sort(key=lambda x: x[1], reverse=True) #sort from highest to lowest score 

        return [
            Event(
                event_type="PEAK_LOUD",
                timestamp=f.window_start,
                duration=f.window_end - f.window_start,
                description=f"Loud vocalization at {f.window_start:.1f}s - {f.window_end:.1f}s",
                confidence=conf / len(detected) if detected else 0.0,
                labels=list({d.label for d in detected}),
            )
            for f, conf, detected in scored[:top_k]
        ]       
        

    #MULTIMODAL EVENT DETECTION/DISCRIPTS

    def off_camera_activity(self, threshold: float = 0.6) -> list[Event]:
        """Nothing detected in the camera but something can be heard off screen"""
        events = []
        for f in self.fused:
            if f.has_visual or not f.audio: #If there is a visual detection or no audio, skip it
                continue
            ratio = self.non_ambient_thresholding(f)
            if ratio >= threshold: #check if confidence of relative non ambient is above threshold
                non_ambient = [detected for detected in f.audio if detected.label not in self.ambient_labels]
                #Add event
                events.append(Event(
                    event_type="OFF_CAMERA_ACTIVITY",
                    timestamp=f.window_start,
                    duration=f.window_end - f.window_start,
                    description=f"Off-camera activity heard at {f.window_start:.1f}s - {f.window_end:.1f}s",
                    confidence=sum(detected.confidence for detected in non_ambient) / len(non_ambient) if non_ambient else 0.0, #give the average confidence score
                    labels=list({detected.label for detected in non_ambient}),
                ))
        return events
    
    def corroborated_sightings(self, threshold: float = 0.6) -> list[Event]:
        """windows where you have both visual and audiot that is not ambient """
        events = []
        for f in self.fused:
            if not f.has_visual or not f.audio: #Needs both audio and visual
                continue
            ratio = self.non_ambient_thresholding(f)
            if ratio >= threshold: #check if confidence of relative non ambient is above threshold
                non_ambient = [detected for detected in f.audio if detected.label not in self.ambient_labels] #get list of non ambient sounds
                visual_conf = sum(detected.confidence for detected in f.visual) / len(f.visual) #get average visual confidence
                audio_conf = sum(detected.confidence for detected in non_ambient) / len(non_ambient) if non_ambient else 0.0 #get average non ambient confidence score
                events.append(Event(
                    event_type="CORROBORATED",
                    timestamp=f.window_start,
                    duration=f.window_end - f.window_start,
                    description=f"Corroborated sighting at {f.window_start:.1f}s - {f.window_end:.1f}s",
                    confidence=(visual_conf + audio_conf) / 2, #avergae between visual and audio confidence
                    labels=list({detected.label for detected in f.visual} | {detected.label for detected in non_ambient}),
                ))
        return events
    
    def generate_all_events(self) -> list[Event]:
        """Gets all events into a single output"""
        events = []
        events.extend(self.entries_and_exits())
        events.extend(self.quiet_periods())
        events.extend(self.peak_loud_windows())
        events.extend(self.off_camera_activity())
        events.extend(self.corroborated_sightings())
        events.sort(key=lambda e: e.timestamp)
        return events

    def print_event_log(self):
        """Print a a timeline of all the events and descriptors """
        events = self.generate_all_events()

        if not events:
            print("No events detected.")
            return

        print(f"\n{'=' * 70}")
        print(f"  SCENE EVENT LOG — {len(events)} events detected")
        print(f"{'=' * 70}\n")

        # Discriptors of the scene rather than events per se 
        print(f"  Animals seen: {self.unique_animal_count()}")
        species = self.species_counts()
        if species:
            species_str = ", ".join(f"{label} ({count})" for label, count in species.items())
            print(f"  Species: {species_str}")

        dominant = self.dominant_sounds()
        if dominant:
            sounds_str = ", ".join(f"{label} ({score:.2f})" for label, score in dominant)
            print(f"  Dominant sounds: {sounds_str}")

        print(f"\n{'-' * 70}")
        print(f"  {'TIME':<12} {'TYPE':<24} {'CONF':<8} {'DESCRIPTION'}")
        print(f"{'-' * 70}")

        for e in events:
            minutes, seconds = divmod(e.timestamp, 60)
            time_str = f"{int(minutes):02d}:{seconds:05.2f}"
            conf_str = f"{e.confidence:.2f}" if e.confidence > 0 else "—"
            print(f"  {time_str:<12} {e.event_type:<24} {conf_str:<8} {e.description}")
            if e.labels:
                print(f"  {'':>12} {'':>24} {'':>8} labels: {', '.join(e.labels)}")

        print(f"\n{'=' * 70}\n")