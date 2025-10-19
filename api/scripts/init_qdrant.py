import requests
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

OLLAMA_URL = "http://ollama:11434/api/embed"
QDRANT_URL = "http://qdrant:6333"

texts = [
    "Tipps zum Energiesparen im Haushalt: Licht ausschalten, Geräte vom Strom trennen.",
    "Nachhaltige Energiequellen wie Solarstrom helfen beim Senken der Stromkosten.",
    "Moderne Smart-Meter-Systeme ermöglichen genaue Verbrauchsanalysen."
]

def get_embedding(text):
    res = requests.post(OLLAMA_URL, json={"model": "nomic-embed-text", "input": text}, timeout=30)
    res.raise_for_status()
    data = res.json()
    return data["embeddings"][0]

client = QdrantClient(host="qdrant", port=6333)

# 1️⃣ Collection anlegen
client.recreate_collection(
    collection_name="documents",
    vectors_config=VectorParams(size=768, distance=Distance.COSINE)
)

# 2️⃣ Texte einfügen
points = []
for i, text in enumerate(texts):
    embedding = get_embedding(text)
    points.append(PointStruct(id=i+1, vector=embedding, payload={"text": text}))

client.upsert(collection_name="documents", points=points)
print("✅ Qdrant initialisiert – Collection 'documents' mit Beispieldaten angelegt.")

