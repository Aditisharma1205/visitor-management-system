import cv2
import os
from datetime import datetime


SNAPSHOT_DIR = "uploads/snapshots"

os.makedirs(
    SNAPSHOT_DIR,
    exist_ok=True
)


def save_snapshot(
    frame,
    bbox,
    prefix,
    name
):

    x1, y1, x2, y2 = map(
        int,
        bbox
    )

    face_crop = frame[
        max(0, y1):max(0, y2),
        max(0, x1):max(0, x2)
    ]

    filename = (
        f"{prefix}_"
        f"{name}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    )

    filepath = os.path.join(
        SNAPSHOT_DIR,
        filename
    )

    cv2.imwrite(
        filepath,
        face_crop
    )

    return filepath