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

    data["timestamp"] = time.time()
    return data
def cleanup_cache():

    current_time = time.time()

    expired = []

    for track_id, data in track_cache.items():

        if (
            current_time
            - data["timestamp"]
            > CACHE_SECONDS
        ):
            expired.append(track_id)

    for track_id in expired:
        del track_cache[track_id]
        
def cache_identity(
    track_id,
    result
):
    cleanup_cache()
    track_cache[track_id] = {
        **result,
        "timestamp": time.time()
    }
    