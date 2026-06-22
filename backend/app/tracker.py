import numpy as np
import time

tracks = {}

next_track_id = 1

TRACK_THRESHOLD = 0.65
POSITION_THRESHOLD = 100
TRACK_TIMEOUT = 10


def cosine_similarity(a, b):

    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)

    return float(np.dot(a, b))


def center_distance(c1, c2):

    return (
        (c1[0] - c2[0]) ** 2 +
        (c1[1] - c2[1]) ** 2
    ) ** 0.5


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
    bbox
):

    cleanup_tracks()

    global next_track_id

    x1, y1, x2, y2 = bbox

    center = (
        (x1 + x2) / 2,
        (y1 + y2) / 2
    )

    best_track = None
    best_similarity = 0

    for track_id, track_data in tracks.items():

        embedding_similarity = cosine_similarity(
            embedding,
            track_data["mean_embedding"]
        )

        position_distance = center_distance(
            center,
            track_data["center"]
        )
        
        print(
        f"TRACK={track_id} "
        f"EMB_SIM={embedding_similarity:.3f} "
        f"POS_DIST={position_distance:.1f}"
        )
        
        if (
            embedding_similarity > best_similarity
            and
            position_distance < POSITION_THRESHOLD
        ):

            best_similarity = embedding_similarity
            best_track = track_id

    if (
        best_track is not None
        and best_similarity > TRACK_THRESHOLD
    ):

        tracks[best_track][
            "embeddings"
        ].append(
            embedding
        )

        tracks[best_track][
            "mean_embedding"
        ] = np.mean(
            tracks[best_track]["embeddings"],
            axis=0
        )

        tracks[best_track][
            "last_seen"
        ] = time.time()

        tracks[best_track][
            "center"
        ] = center

        return best_track

    track_id = next_track_id
    
    next_track_id += 1

    tracks[track_id] = {
        "embeddings": [embedding],
        "mean_embedding": embedding,
        "center": center,
        "last_seen": time.time()
    }

    return track_id