import chromadb
import numpy as np

client = chromadb.PersistentClient(
    path="chroma_db"
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

    embedding = np.array(
        embedding
    )

    embedding = (
        embedding
        / np.linalg.norm(
            embedding
        )
    )
    
    print(
    collection.count()  
    )

    result = collection.query(
        query_embeddings=[
            embedding.tolist()
        ],
        n_results=1
    )

    print("CHROMA QUERY RESULT:")
    print(result)

    if not result["ids"][0]:
        return None, 0

    user_id = int(
        result["ids"][0][0]
    )

    distance = result[
        "distances"
    ][0][0]

    similarity = 1 - distance

    print(
        f"USER_ID={user_id}"
    )

    print(
        f"DISTANCE={distance}"
    )

    print(
        f"SIMILARITY={similarity}"
    )

    return (
        user_id,
        similarity
    )