import numpy as np


def aggregate_embeddings(
    embeddings
):

    if len(embeddings) == 0:
        return None

    aggregated_embedding = np.mean(
        embeddings,
        axis=0
    )

    norm = np.linalg.norm(
        aggregated_embedding
    )

    if norm == 0:
        return None

    return (
        aggregated_embedding
        / norm
    )