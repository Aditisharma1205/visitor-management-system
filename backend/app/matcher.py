import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings


def find_best_match(query_embedding, users):

    best_similarity = -1
    best_user = None

    for user in users:

        if not os.path.exists(user.embedding_path):
            continue

        stored_embedding = np.load(
            user.embedding_path
        )

        similarity = cosine_similarity(
            query_embedding.reshape(1, -1),
            stored_embedding.reshape(1, -1)
        )[0][0]

        if similarity > best_similarity:

            best_similarity = similarity
            best_user = user

    if best_similarity >= settings.threshold:

        return best_user, best_similarity

    return None, best_similarity