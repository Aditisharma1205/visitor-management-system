import time

CACHE_SECONDS = 10

track_cache = {}
def get_cached_identity(track_id):

    if track_id not in track_cache:
        return None

    data = track_cache[track_id]

    if (
        time.time()
        - data["timestamp"]
        > CACHE_SECONDS
    ):
        del track_cache[track_id]
        return None

    return data
def cache_identity(
    track_id,
    result
):

    track_cache[track_id] = {
        **result,
        "timestamp": time.time()
    }