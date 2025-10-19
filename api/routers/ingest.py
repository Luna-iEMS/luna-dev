from fastapi import APIRouter, UploadFile, File, HTTPException
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, PointStruct
import requests
import hashlib
import os
import psycopg
import uuid
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api/v1/ingest", tags=["ingest"])

# ------------------------------------------------------------
# 🔧 Verbindungen & Konstanten
# ------------------------------------------------------------
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": os.getenv("DB_PORT", "5432"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "dbname": os.getenv("DB_NAME", "luna"),
}

QDRANT_CONFIG = {
    "host": os.getenv("QDRANT_HOST", "qdrant"),
    "port": int(os.getenv("QDRANT_PORT", 6333))
}

DOCS_PATH = "/home/mp/iems-luna/docs-luna"
TIKA_URL = "http://tika:9998/tika"
EMBED_URL = "http://ollama:11434/api/embed"
COLLECTION = "documents"


# ------------------------------------------------------------
# 🧠 Hilfsfunktionen
# ------------------------------------------------------------
def file_hash(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


def extract_text_tika(file_bytes: bytes) -> str:
    """Extrahiere Text aus Datei via Apache Tika"""
    try:
        headers = {"Accept": "text/plain"}
        response = requests.put(TIKA_URL, data=file_bytes, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tika-Fehler: {str(e)}")


def get_embedding_ollama(text: str):
    """Erstelle Embedding via Ollama"""
    try:
        response = requests.post(
            EMBED_URL,
            json={"model": "nomic-embed-text", "input": text},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data["embeddings"][0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama-Fehler: {str(e)}")


def ensure_qdrant_collection(client: QdrantClient):
    """Erstellt Collection, falls nicht vorhanden"""
    try:
        collections = [c.name for c in client.get_collections().collections]
        if COLLECTION not in collections:
            client.create_collection(
                collection_name=COLLECTION,
                vectors_config=VectorParams(size=768, distance="Cosine")
            )
            print(f"🟢 Qdrant-Collection '{COLLECTION}' erstellt.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Qdrant-Init-Fehler: {str(e)}")


# ------------------------------------------------------------
# 📤 Einzelner Datei-Upload
# ------------------------------------------------------------
@router.post("/doc")
async def upload_doc(files: List[UploadFile] = File(...)):
    qdrant = QdrantClient(**QDRANT_CONFIG)
    ensure_qdrant_collection(qdrant)

    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            for file in files:
                try:
                    file_bytes = await file.read()
                    sha256 = file_hash(file_bytes)

                    # Prüfen, ob Datei schon existiert
                    cur.execute("SELECT item_id FROM items WHERE sha256 = %s;", (sha256,))
                    if cur.fetchone():
                        print(f"⚪ Datei '{file.filename}' bereits vorhanden.")
                        continue

                    text = extract_text_tika(file_bytes)
                    if not text.strip():
                        raise HTTPException(status_code=400, detail=f"Keine Textdaten in {file.filename}")

                    embedding = get_embedding_ollama(text)

                    # In Postgres speichern
                    cur.execute("""
                        INSERT INTO items (kind, source, title, tags, filename, sha256, content, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                        ON CONFLICT (sha256) DO NOTHING;
                    """, (
                        "document",
                        "upload",
                        file.filename,
                        [],
                        file.filename,
                        sha256,
                        text
                    ))

                    # In Qdrant speichern – mit UUID als ID
                    qdrant.upsert(
                        collection_name=COLLECTION,
                        points=[PointStruct(
                            id=str(uuid.uuid4()),
                            vector=embedding,
                            payload={
                                "filename": file.filename,
                                "text": text,
                                "sha256": sha256
                            }
                        )]
                    )
                    print(f"✅ Datei '{file.filename}' erfolgreich verarbeitet.")

                except Exception as e:
                    conn.rollback()
                    raise HTTPException(status_code=500, detail=f"Fehler bei {file.filename}: {str(e)}")

        conn.commit()
    return {"status": "ok", "message": "Upload abgeschlossen"}


# ------------------------------------------------------------
# 🤖 Automatische Ingestion
# ------------------------------------------------------------
@router.post("/auto")
def auto_ingest():
    qdrant = QdrantClient(**QDRANT_CONFIG)
    ensure_qdrant_collection(qdrant)

    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            if not os.path.exists(DOCS_PATH):
                raise HTTPException(status_code=404, detail=f"Pfad {DOCS_PATH} nicht gefunden")

            files = [f for f in os.listdir(DOCS_PATH) if f.endswith(".md")]
            if not files:
                raise HTTPException(status_code=404, detail="Keine Markdown-Dateien gefunden")

            for fname in files:
                fpath = os.path.join(DOCS_PATH, fname)
                try:
                    with open(fpath, "rb") as f:
                        file_bytes = f.read()
                    sha256 = file_hash(file_bytes)

                    cur.execute("SELECT item_id FROM items WHERE sha256 = %s;", (sha256,))
                    if cur.fetchone():
                        print(f"⚪ Datei '{fname}' bereits vorhanden.")
                        continue

                    text = extract_text_tika(file_bytes)
                    if not text.strip():
                        continue

                    embedding = get_embedding_ollama(text)

                    cur.execute("""
                        INSERT INTO items (kind, source, title, tags, filename, sha256, content, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                        ON CONFLICT (sha256) DO NOTHING;
                    """, (
                        "document",
                        "auto_ingest",
                        fname,
                        [],
                        fname,
                        sha256,
                        text
                    ))

                    qdrant.upsert(
                        collection_name=COLLECTION,
                        points=[PointStruct(
                            id=str(uuid.uuid4()),  # ✅ eindeutige ID
                            vector=embedding,
                            payload={
                                "filename": fname,
                                "text": text,
                                "sha256": sha256
                            }
                        )]
                    )
                    print(f"✅ Auto-Ingest: '{fname}' erfolgreich verarbeitet.")

                except Exception as e:
                    conn.rollback()
                    raise HTTPException(status_code=500, detail=f"Fehler bei {fname}: {str(e)}")

        conn.commit()
    return {"status": "ok", "message": "Alle Markdown-Dateien verarbeitet."}
