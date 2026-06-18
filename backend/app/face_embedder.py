import cv2
from insightface.app import FaceAnalysis

face_app = FaceAnalysis()
face_app.prepare(ctx_id=0)

def extract_embedding(image_path):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Image not found")

    faces = face_app.get(image)

    if not faces:
        return None

    return faces[0].embedding
