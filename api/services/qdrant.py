import qdrant_client
from qdrant_client import models as qm

COLL = "luna_chunks"

def get_client():
    return qdrant_client.QdrantClient(host="luna_qdrant", port=6333)

def ensure_collection(dim: int):
    c = get_client()
    try:
        c.get_collection(COLL)
    except Exception:
        c.recreate_collection(
            collection_name=COLL,
            vectors_config=qm.VectorParams(size=dim, distance=qm.Distance.COSINE),
        )
    return c

def upsert_vectors(ids, vectors, payloads):
    c = get_client()
    c.upsert(
        collection_name=COLL,
        points=qm.Batch(ids=[str(i) for i in ids], vectors=vectors, payloads=payloads),
    )

def search(vector, top_k=5):
    c = get_client()
    return c.search(collection_name=COLL, query_vector=vector, limit=top_k)

