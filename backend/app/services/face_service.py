import cv2
from insightface.app import FaceAnalysis

face_app = FaceAnalysis(name="buffalo_l")

face_app.prepare(
    ctx_id=-1,
    det_size=(320, 320)
)


def get_embedding(image_path: str):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Unable to read image")

    faces = face_app.get(image)

    if len(faces) == 0:
        raise ValueError("No face detected")

    if len(faces) > 1:
        raise ValueError("Multiple faces detected")

    return faces[0].embedding


def detect_faces(image_path: str):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Unable to read image")

    faces = face_app.get(image)

    if len(faces) == 0:
        return []

    results = []

    for face in faces:
        results.append({
            "embedding": face.embedding,
            "bbox": face.bbox.astype(int).tolist()
        })

    return results

def detect_faces_from_frame(image):

    original_h, original_w = image.shape[:2]

    resized = cv2.resize(
        image,
        (320, 240),
        interpolation=cv2.INTER_AREA
    )

    scale_x = original_w / 320
    scale_y = original_h / 240

    faces = face_app.get(resized)

    results = []

    for face in faces:

        bbox = face.bbox.astype(int)

        bbox = [
            int(bbox[0] * scale_x),
            int(bbox[1] * scale_y),
            int(bbox[2] * scale_x),
            int(bbox[3] * scale_y),
        ]

        results.append(
            {
                "embedding": face.embedding,
                "bbox": bbox
            }
        )

    return results