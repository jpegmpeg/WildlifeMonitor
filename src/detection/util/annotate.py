"""
Allows for video annoation after detection by drawing a 
bounding box on the detected element and identifying the animal with confidence 
"""

import cv2
import numpy as np

def _color_for_id(track_id: int | None) -> tuple[int, int, int]:
    """Consistent BGR color per track_id so the same animal keeps its color"""
    if track_id is None:
        return (200, 200, 200)  # grey for untracked
    #golden-ratio hash -> well-spaced hues
    hue = int((track_id * 0.6180339887) % 1.0 * 180)
    hsv = np.uint8([[[hue, 220, 230]]])
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0, 0]
    return int(bgr[0]), int(bgr[1]), int(bgr[2])


def draw_detections(frame: np.ndarray, detections: list) -> np.ndarray:
    """Draw boudning box on the frame being processed"""

    for d in detections:
        color = _color_for_id(d.track_id) #assign a color for the track_id
        #get coordinates from the bounding box
        x1, y1 = int(d.box.x1), int(d.box.y1)  
        x2, y2 = int(d.box.x2), int(d.box.y2)

        # creat a rectange based on the bounding box and the color, 2 thickness
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        #label e.g. "#3 deer 87%"
        id_str = f"#{d.track_id}: " if d.track_id is not None else ""
        label = f"{id_str}{d.label} {d.confidence * 100:.0f}%"

        #text background for readability; tw is text width and th is text height, baseline is extra pixels below baseline
        (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        #figure out where the top of the the text is, 4 is extra padding to make text not touch the box
        top = max(y1 - th - baseline - 4, 0)
        #small box to write the text in
        cv2.rectangle(frame, (x1, top), (x1 + tw + 4, y1), color, -1)
        #write the text
        cv2.putText(frame, label, (x1 + 2, y1 - 4),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2, cv2.LINE_AA,)
    return frame