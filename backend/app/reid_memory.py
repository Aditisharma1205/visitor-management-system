import time
import numpy as np

MEMORY_TIMEOUT = 600

memory = {}

def cosine_similarity(a, b):

    a = a / np.linalg.norm(a)

    b = b / np.linalg.norm(b)

    return float(np.dot(a, b))

def save_identity(
    user_id,
    name,
    embedding
):

    memory[user_id] = {

        "name": name,

        "embedding": embedding,

        "timestamp": time.time()
    }
    
def search_memory(
    embedding
):

    best_user = None

    best_similarity = 0

    current_time = time.time()

    expired = []

    for user_id, data in memory.items():

        if (
            current_time -
            data["timestamp"]
            > MEMORY_TIMEOUT
        ):
            expired.append(user_id)
            continue

        similarity = cosine_similarity(
            embedding,
            data["embedding"]
        )

        if similarity > best_similarity:

            best_similarity = similarity

            best_user = user_id

    for user_id in expired:

        del memory[user_id]

    return (
        best_user,
        best_similarity
    )