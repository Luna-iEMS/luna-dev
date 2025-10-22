import os
import uuid
from qdrant_client import QdrantClient, models as qm

__all__ = ["client", "ensure_collection", "upsert_vectors", "search", "qm"]

# === Qdrant Konfiguration ===
COLL = os.getenv("QDRANT_COLLECTION", "luna_chunks")
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_HTTP = int(os.getenv("QDRANT_HTTP", "6333"))

# Automatische URL-Erkennung
# Wenn Host bereits mit http:// beginnt, nutze `url=`, sonst klassisch host/port
if QDRANT_HOST.startswith("http"):
    client = QdrantClient(url=QDRANT_HOST)
else:
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_HTTP)

# -------------------------------------------------------------
# Collection sicherstellen
# -------------------------------------------------------------
def ensure_collection(dim: int = 384):
    """Erstellt oder prüft, ob die Collection existiert."""
    try:
        collections = client.get_collections().collections
        if any(c.name == COLL for c in collections):
            print(f"✅ Qdrant-Collection '{COLL}' existiert bereits.")
            return
        print(f"📦 Erstelle neue Qdrant-Collection '{COLL}' (dim={dim}) …")
        client.recreate_collection(
            collection_name=COLL,
            vectors_config=qm.VectorParams(
                size=dim,
                distance=qm.Distance.COSINE
            ),
        )
        print(f"✅ Collection '{COLL}' erfolgreich erstellt.")
    except Exception as e:
        print(f"⚠️ Fehler beim Qdrant-Setup: {e}")

# -------------------------------------------------------------
# Vektoren hochladen / upsert
# -------------------------------------------------------------
def upsert_vectors(texts, vectors, payloads=None):
    """Speichert Embeddings in Qdrant."""
    try:
        if not vectors:
            print("⚠️ Keine Vektoren übergeben – kein Upload durchgeführt.")
            return

        if payloads is None:
            payloads = [{"text": t} for t in texts]

        # Punkt-IDs als UUIDs erzeugen
        points = [
            qm.PointStruct(
                id=str(uuid.uuid4()),
                vector=vec,
                payload=payload
            )
            for vec, payload in zip(vectors, payloads)
        ]

        result = client.upsert(collection_name=COLL, points=points)
        print(f"✅ {len(points)} Vektoren erfolgreich in Qdrant upserted. Ergebnis: {result.status}")
        return result

    except Exception as e:
        print(f"⚠️ Fehler beim Upsert in Qdrant: {e}")

# -------------------------------------------------------------
# Ähnlichkeitssuche
# -------------------------------------------------------------
def search(vector, top_k=6):
    """Sucht ähnliche Einträge zu einem gegebenen Vektor."""
    try:
        return client.search(collection_name=COLL, query_vector=vector, limit=top_k)
    except Exception as e:
        print(f"⚠️ Qdrant-Suche fehlgeschlagen: {e}")
        return []



# -------------------------------------------------------------
# Vektoren hochladen
# -------------------------------------------------------------
def upsert_vectors(texts, vectors, payloads=None):
    """Speichert Text-Embeddings in Qdrant mit optionalen Payloads."""
    try:
        c = get_client()
        if not vectors:
            print("⚠️ Keine Vektoren übergeben – kein Upload durchgeführt.")
            return

        if payloads is None:
            payloads = [{"text": t} for t in texts]

        # Erzeuge eindeutige UUIDs für alle Punkte
        point_ids = [str(uuid.uuid4()) for _ in range(len(vectors))]

        points = [
            qm.PointStruct(id=pid, vector=vec, payload=pl)
            for pid, vec, pl in zip(point_ids, vectors, payloads)
        ]

        result = c.upsert(collection_name=COLL, points=points)
        print(f"✅ {len(points)} Embeddings in Qdrant gespeichert. Ergebnis: {result.status}")

    except Exception as e:
        print(f"⚠️ Fehler beim Upsert in Qdrant: {e}")


# -------------------------------------------------------------
# Suche
# -------------------------------------------------------------
def search(vector, top_k=6):
    """Sucht ähnliche Einträge zu einem Vektor."""
    c = get_client()
    try:
        return c.search(collection_name=COLL, query_vector=vector, limit=top_k)
    except Exception as e:
        print(f"⚠️ Qdrant-Suche fehlgeschlagen: {e}")
        return []

