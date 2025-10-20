import os
from qdrant_client import QdrantClient, models as qm

# === Qdrant Konfiguration ===
COLL = os.getenv("QDRANT_COLLECTION", "luna_chunks")
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_HTTP = int(os.getenv("QDRANT_HTTP", "6333"))


def get_client():
    """Erstellt einen QdrantClient mit Host/Port aus Umgebungsvariablen."""
    return QdrantClient(host=QDRANT_HOST, port=QDRANT_HTTP)


def ensure_collection(dim: int = 384):
    """Stellt sicher, dass die Collection existiert (oder legt sie an)."""
    c = get_client()
    try:
        c.get_collection(COLL)
        print(f"✅ Qdrant-Collection '{COLL}' existiert bereits.")
    except Exception:
        print(f"⚙️ Erstelle neue Qdrant-Collection '{COLL}' mit dim={dim}")
        c.recreate_collection(
            collection_name=COLL,
            vectors_config=qm.VectorParams(size=dim, distance=qm.Distance.COSINE),
        )
    return c


def upsert_vectors(texts, vectors, payloads=None):
    """Speichert Text-Embeddings in Qdrant mit optionalen Payloads."""
    try:
        c = get_client()
        if payloads is None:
            payloads = [{"text": t} for t in texts]

        ids = [str(i) for i in range(len(vectors))]
        points = qm.Batch(ids=ids, vectors=vectors, payloads=payloads)
        c.upsert(collection_name=COLL, points=points)
        print(f"✅ {len(vectors)} Embeddings in Qdrant gespeichert.")
    except Exception as e:
        print(f"⚠️ Fehler beim Upsert in Qdrant: {e}")


def search(vector, top_k=6):
    """Sucht ähnliche Einträge zu einem Vektor."""
    c = get_client()
    try:
        return c.search(collection_name=COLL, query_vector=vector, limit=top_k)
    except Exception as e:
        print(f"⚠️ Qdrant-Suche fehlgeschlagen: {e}")
        return []

