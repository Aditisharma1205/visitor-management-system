import numpy as np
import time

tracks = {}

next_track_id = 1

TRACK_THRESHOLD = 0.5
TRACK_TIMEOUT = 10
MAX_TRACK_EMBEDDINGS = 10

# Position gating is expressed as a multiple of face size (bbox diagonal),
# not a fixed pixel count. A face that fills most of a 640x480 frame can
# easily move >100px between two 300ms-apart frames just from head tilt,
# so a fixed threshold was splitting one face into multiple tracks.
POSITION_THRESHOLD_FACTOR = 1.5

# If embedding similarity is very high, allow an even looser position gate
# (handles fast head movement without losing track identity).
HIGH_CONFIDENCE_SIMILARITY = 0.8
HIGH_CONFIDENCE_POSITION_FACTOR = 3.0


def cosine_similarity(a, b):

    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)

    return float(np.dot(a, b))


def center_distance(c1, c2):

    return (
        (c1[0] - c2[0]) ** 2 +
        (c1[1] - c2[1]) ** 2
    ) ** 0.5


def bbox_diagonal(bbox):

    x1, y1, x2, y2 = bbox

    return (
        (x2 - x1) ** 2 +
        (y2 - y1) ** 2
    ) ** 0.5


def intersection_over_union(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interWidth = max(0, xB - xA)
    interHeight = max(0, yB - yA)
    interArea = interWidth * interHeight

    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    unionArea = float(boxAArea + boxBArea - interArea)
    if unionArea == 0:
        return 0.0

    return interArea / unionArea


def cleanup_tracks():

    current_time = time.time()

    expired_tracks = []

    for track_id, track_data in tracks.items():

        if (
            current_time
            - track_data["last_seen"]
            > TRACK_TIMEOUT
        ):
            expired_tracks.append(track_id)

    for track_id in expired_tracks:

        del tracks[track_id]


def assign_track(
    embedding,
    bbox,
    exclude_track_ids=None
):

    cleanup_tracks()

    global next_track_id

    if exclude_track_ids is None:
        exclude_track_ids = []

    x1, y1, x2, y2 = bbox

    center = (
        (x1 + x2) / 2,
        (y1 + y2) / 2
    )

    face_size = bbox_diagonal(bbox)

    best_track = None
    best_cost = -1.0
    best_similarity = 0

    for track_id, track_data in tracks.items():
        if track_id in exclude_track_ids:
            continue

        embedding_similarity = cosine_similarity(
            embedding,
            track_data["mean_embedding"]
        )

        position_distance = center_distance(
            center,
            track_data["center"]
        )

        # Gate scales with face size so a large/close face isn't penalized
        # for normal movement, and a small/far face stays tightly gated.
        reference_size = max(face_size, track_data["size"])

        if embedding_similarity >= HIGH_CONFIDENCE_SIMILARITY:
            position_gate = reference_size * HIGH_CONFIDENCE_POSITION_FACTOR
        else:
            position_gate = reference_size * POSITION_THRESHOLD_FACTOR

        if position_distance < position_gate:
            track_bbox = track_data.get("bbox")
            if track_bbox is None:
                tc = track_data["center"]
                ts = track_data["size"]
                w = 0.8 * ts
                h = 0.6 * ts
                track_bbox = [tc[0] - w/2, tc[1] - h/2, tc[0] + w/2, tc[1] + h/2]

            iou_score = intersection_over_union(bbox, track_bbox)
            center_distance_score = max(0.0, 1.0 - (position_distance / reference_size))

            cost = (
                0.6 * embedding_similarity +
                0.3 * iou_score +
                0.1 * center_distance_score
            )

            if cost > best_cost:
                best_cost = cost
                best_track = track_id
                best_similarity = embedding_similarity

    if (
        best_track is not None
        and best_similarity > TRACK_THRESHOLD
    ):

        track = tracks[best_track]

        track["embeddings"].append(embedding)

        if len(track["embeddings"]) > MAX_TRACK_EMBEDDINGS:
            track["embeddings"].pop(0)

        track["mean_embedding"] = np.mean(
            track["embeddings"],
            axis=0
        )
        track["previous_center"] = track["center"]
        track["last_seen"] = time.time()
        track["center"] = center
        track["size"] = face_size
        track["bbox"] = bbox

        print(
    f"MATCHED TRACK {best_track} "
    f"SIM={best_similarity:.3f} "
    f"COST={best_cost:.3f}"
)
        return best_track

    track_id = next_track_id

    next_track_id += 1

    tracks[track_id] = {
    "embeddings": [embedding],
    "mean_embedding": embedding,
    "center": center,
    "size": face_size,
    "last_seen": time.time(),
    "previous_zone": None,
    "current_zone": None,
    "first_zone": None,
    "unknown_visitor": None,
    "bbox": bbox
}
    print(f"NEW TRACK {track_id}")
    return track_id

def get_track(track_id):

    return tracks.get(track_id)