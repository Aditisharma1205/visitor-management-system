import cv2
import uuid
import os

def save_unknown_face(
    image_path,
    bbox
):

    image = cv2.imread(
        image_path
    )

    x1, y1, x2, y2 = map(
        int,
        bbox
    )

    face_crop = image[
        y1:y2,
        x1:x2
    ]

    os.makedirs(
        "uploads/unknown",
        exist_ok=True
    )

    filename = (
        f"{uuid.uuid4()}.jpg"
    )

    save_path = os.path.join(
        "uploads/unknown",
        filename
    )

    cv2.imwrite(
        save_path,
        face_crop
    )

    return save_path