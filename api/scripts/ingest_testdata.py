import requests
from qdrant_client import QdrantClient, models
import os

# Konfiguration
OLLAMA_URL = "http://ollama:11434/api/embed"
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
COLLECTION_NAME = "documents"

def embed(text: str):
    """Sendet Text an Ollama, um Embedding zu erzeugen."""
    payload = {
        "model": "nomic-embed-text",
        "input": text
    }
    print(f"➡️  Sende Anfrage an {OLLAMA_URL} ...")
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        embedding = data.get("embedding") or data.get("embeddings")

        # Sicherheitscheck
        if not embedding:
            raise ValueError(f"❌ Keine Embedding-Daten zurückgegeben: {data}")

        # Flatten falls nested
        if isinstance(embedding[0], list):
            embedding = embedding[0]

        return embedding
    except Exception as e:
        raise RuntimeError(f"Fehler beim Erstellen des Embeddings: {e}")

def main():
    print(f"🌐 Verbinde zu Ollama unter: {OLLAMA_URL}")
    print(f"🧠 Verbinde zu Qdrant unter: {QDRANT_HOST}:6333")

    qdrant = QdrantClient(host=QDRANT_HOST, port=6333)
    print(f"🆕 Erstelle Collection '{COLLECTION_NAME}' ...")

    # Warnung unterdrücken, bis du Qdrant-Image updatest
    qdrant.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE)
    )

    texts = [
        "Energiepreise steigen in Österreich 2025 erneut.",
        "Photovoltaik wird immer wichtiger für die Energiewende.",
        "Stromverbrauch von Haushalten sinkt leicht im Jahresvergleich."
    ]

    for i, text in enumerate(texts, start=1):
        print(f"🔹 Erstelle Embedding für Satz {i} ...")
        emb = embed(text)
        qdrant.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                models.PointStruct(id=i, vector=emb, payload={"text": text})
            ]
        )

    print("✅ Fertig! Alle Texte wurden erfolgreich in Qdrant gespeichert.")

if __name__ == "__main__":
    main()

