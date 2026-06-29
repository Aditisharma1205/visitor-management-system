import os
import cv2
from datetime import datetime


ENTRY_DIR = "uploads/snapshots/entry"
EXIT_DIR = "uploads/snapshots/exit"

os.makedirs(ENTRY_DIR, exist_ok=True)
os.makedirs(EXIT_DIR, exist_ok=True)


def save_snapshot(
    frame,
    bbox,
    event_type,
    identity
):
    """
    frame -> full webcam frame (numpy array)

    bbox -> [x1,y1,x2,y2]

    event_type -> entry / exit

    identity -> user name or Unknown_001

    returns saved image path
    """

    x1, y1, x2, y2 = bbox

    h, w = frame.shape[:2]

    x1 = max(0, int(x1))
    y1 = max(0, int(y1))
    x2 = min(w, int(x2))
    y2 = min(h, int(y2))

    face_crop = frame[y1:y2, x1:x2]

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"{identity}_{timestamp}.jpg"
    )

    if event_type == "entry":
        save_dir = ENTRY_DIR
    else:
        save_dir = EXIT_DIR

    path = os.path.join(
        save_dir,
        filename
    )

    cv2.imwrite(
        path,
        face_crop
    )

    return path