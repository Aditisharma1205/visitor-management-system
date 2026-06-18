clusters = {}

MAX_CLUSTER_SIZE = 10


def add_to_cluster(
    track_id,
    embedding
):
    if track_id not in clusters:
        clusters[track_id] = []

    clusters[track_id].append(
        embedding
    )

    if len(clusters[track_id]) > MAX_CLUSTER_SIZE:
        clusters[track_id].pop(0)


def get_cluster(
    track_id
):

    return clusters.get(
        track_id,
        []
    )


def get_cluster_size(
    track_id
):

    return len(
        clusters.get(
            track_id,
            []
        )
    )


def clear_cluster(track_id):

    if track_id in clusters:
        del clusters[track_id]