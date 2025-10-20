import os, time
from qdrant_client import QdrantClient, models as qm

QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_HTTP", 6333))
COLLECTION_NAME = "luna_docs"
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

def ensure_collection(dim: int = 384):
    """Stellt sicher, dass die Qdrant-Collection existiert."""
    try:
        if COLLECTION_NAME not in [c.name for c in client.get_collections().collections]:
            print(f"⚙️ Erstelle neue Qdrant-Collection '{COLLECTION_NAME}' mit dim={dim}")
            client.recreate_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=qm.VectorParams(size=dim, distance=qm.Distance.COSINE),
            )
    except Exception as e:
        print(f"⚠️ Qdrant-Collection konnte nicht erstellt werden: {e}")

def upsert_vectors(texts, vectors):
    """Speichert Embeddings in Qdrant."""
    points = [
        qm.PointStruct(id=i, vector=v, payload={"text": t})
        for i, (t, v) in enumerate(zip(texts, vectors))
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=points)
