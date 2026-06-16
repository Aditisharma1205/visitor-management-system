import os
import faiss
import numpy as np

INDEX_PATH = "faiss_index/index.faiss"
MAPPING_PATH = "faiss_index/user_mapping.npy"

EMBEDDING_DIM = 512


def load_or_create_index():

    os.makedirs("faiss_index", exist_ok=True)

    if os.path.exists(INDEX_PATH):

        index = faiss.read_index(INDEX_PATH)

    else:

        index = faiss.IndexFlatIP(
            EMBEDDING_DIM
        )

    return index


def load_mapping():

    if os.path.exists(MAPPING_PATH):

        return np.load(
            MAPPING_PATH,
            allow_pickle=True
        ).tolist()

    return []


def save_mapping(mapping):

    np.save(
        MAPPING_PATH,
        np.array(mapping)
    )


def save_index(index):

    faiss.write_index(
        index,
        INDEX_PATH
    )
def add_embedding(
    embedding,
    user_id
):

    index = load_or_create_index()

    mapping = load_mapping()

    embedding = embedding.astype(
        np.float32
    )

    embedding = embedding.reshape(
        1,
        -1
    )

    faiss.normalize_L2(
        embedding
    )

    index.add(
        embedding
    )

    mapping.append(
        user_id
    )

    save_index(index)

    save_mapping(mapping)

def search_embedding(
    embedding
):

    index = load_or_create_index()

    mapping = load_mapping()

    if index.ntotal == 0:

        return None, 0

    embedding = embedding.astype(
        np.float32
    )

    embedding = embedding.reshape(
        1,
        -1
    )

    faiss.normalize_L2(
        embedding
    )

    similarity, indices = index.search(
        embedding,
        1
    )

    score = similarity[0][0]

    idx = indices[0][0]

    if idx == -1:

        return None, score

    return mapping[idx], score

def search_embedding(embedding):

    index = load_or_create_index()

    mapping = load_mapping()

    if index.ntotal == 0:

        return None, 0.0

    embedding = embedding.astype(
        np.float32
    )

    embedding = embedding.reshape(
        1,
        -1
    )

    faiss.normalize_L2(
        embedding
    )

    similarities, indices = index.search(
        embedding,
        1
    )

    similarity = similarities[0][0]

    idx = indices[0][0]

    if idx == -1:

        return None, similarity

    return mapping[idx], similarity