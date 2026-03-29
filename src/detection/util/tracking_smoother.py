"""
The labels during tracking for a specific entity can sometimes change through frames. 
the goal is to smooth tracking label so that the most common label assigned propogates within a 
certain time window to smooth tracking
"""

from collections import defaultdict, Counter

class TrackClassSmoother:
    """use majority label classification to smooth labeling across time in a window for a given entity"""

    def __init__(self, window_size=15):
        self.history = defaultdict(list) #keeps track of track_ids and labels
        self.window_size = window_size #number of frames the track_id appears in 

    def smooth(self, detections: list) -> list:
        """implements the smoothing to give majority label"""
        for detection in detections:
            if detection.track_id is None: 
                continue
            hist = self.history[detection.track_id] #Get the dict location for the track_id
            hist.append(detection.label) #append the relevant label  to that track_id key in the dict
            if len(hist) > self.window_size: #Once we get to a certain point we restart, so that local frames are more important
                hist.pop(0) #restart track
            most_common = Counter(hist).most_common(1)[0][0]
            detection.label = most_common #assign most common label
        return detections
