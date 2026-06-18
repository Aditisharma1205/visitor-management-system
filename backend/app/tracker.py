import numpy as np

tracks = {}

next_track_id = 1

TRACK_THRESHOLD = 0.75


def cosine_similarity(a, b):

    a = a / np.linalg.norm(a)

    b = b / np.linalg.norm(b)

    return np.dot(a, b)


def assign_track(embedding):

    global next_track_id

    best_track = None

    best_similarity = 0

    for track_id, track_data in tracks.items():

        similarity = cosine_similarity(
            embedding,
            track_data["mean_embedding"]
        )

        if similarity > best_similarity:

            best_similarity = similarity

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

        return best_track

    track_id = next_track_id

    next_track_id += 1

    tracks[track_id] = {
        "embeddings": [embedding],
        "mean_embedding": embedding
    }

    return track_id