import chromadb
import numpy as np

from app.config import settings

client = chromadb.PersistentClient(
    path=settings.chroma_path
)

collection = client.get_or_create_collection(
    name="users",
    metadata={"hnsw:space": "cosine"}
)

def add_embedding(
    embedding,
    user_id,
    name
):
    embedding = np.array(embedding)
    embedding = embedding / np.linalg.norm(embedding)
    collection.add(
        ids=[str(user_id)],
        embeddings=[
            embedding.tolist()
        ],
        metadatas=[
            {
                "user_id": user_id,
                "name": name
            }
        ]
    )
    
def search_embedding(
    embedding
):

    if collection.count() == 0:
        return None, 0

    embedding = np.array(
        embedding
    )

    embedding = (
        embedding
        / np.linalg.norm(
            embedding
        )
    )

    result = collection.query(
        query_embeddings=[embedding.tolist()],
        n_results=1
    )

    if not result["ids"][0]:
        return None, 0

    user_id = int(
        result["ids"][0][0]
    )

    distance = result[
        "distances"
    ][0][0]

    similarity = 1 - distance

    return (
        user_id,
        similarity
    )


def delete_embedding(user_id):
    """Remove a user's embedding from Chroma (call this on user delete)."""
    collection.delete(ids=[str(user_id)])