#!/usr/bin/env python3
"""
🌙 Luna IEMS – Training Pipeline
Liest Dateien aus /data/incoming, erzeugt Embeddings und speichert sie in Qdrant.
"""

import os
import sys
import uuid
import logging
from pathlib import Path
from datetime import datetime

# -------------------------------------------------------------
# Fallback, falls PYTHONPATH nicht gesetzt ist (lokale Läufe)
# -------------------------------------------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.services import embed, qdrant  # noqa: E402

# -------------------------------------------------------------
# Pfade & Logging
# -------------------------------------------------------------
DATA_DIR = Path(os.getenv("DATA_DIR", "/data/incoming"))
MODEL_DIR = Path(os.getenv("MODEL_DIR", "/models/versions"))
LOG_FILE = Path(os.getenv("LOG_FILE", "/logs/train_pipeline.log"))

MODEL_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

console = logging.getLogger("train_pipeline.console")
console.addHandler(logging.StreamHandler(sys.stdout))
console.setLevel(logging.INFO)


# -------------------------------------------------------------
# Hilfsfunktionen
# -------------------------------------------------------------
def discover_texts():
    """Sucht .txt und .md Dateien im DATA_DIR"""
    files = [p for p in DATA_DIR.rglob("*") if p.is_file() and p.suffix.lower() in {".txt", ".md"}]
    logging.info(f"{len(files)} Quelldateien gefunden.")
    return files


# -------------------------------------------------------------
# Trainingslogik
# -------------------------------------------------------------
def retrain_model():
    start_time = datetime.utcnow()
    logging.info("==== Retraining gestartet ====")
    files = discover_texts()

    if not files:
        logging.warning("Keine neuen Daten gefunden – Abbruch.")
        return

    vectors, payloads, texts = [], [], []
    for idx, path in enumerate(files, start=1):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore").strip()
            if not text:
                logging.warning(f"⚠️ Datei {path.name} ist leer, übersprungen.")
                continue

            emb = embed.embed_texts([text])[0]
            vectors.append(emb)
            texts.append(text)

            payloads.append({
                "path": str(path),
                "chunk_id": str(uuid.uuid4()),
                "text": text[:1000],
                "filename": path.name,
            })

            logging.info(f"✅ Datei {idx}/{len(files)} verarbeitet: {path.name}")

        except Exception as e:
            logging.error(f"❌ Fehler beim Verarbeiten von {path.name}: {e}")

    if not vectors:
        logging.warning("Keine Embeddings generiert – kein Upload zu Qdrant.")
        return

    # ---------------------------------------------------------
    # Qdrant – Collection anlegen / aktualisieren
    # ---------------------------------------------------------
    dim = len(vectors[0])
    client = qdrant.ensure_collection(dim=dim)
    logging.info(f"Qdrant-Collection initialisiert (dim={dim}).")

    try:
        # Punkt-IDs als UUIDs erzeugen
        points = [
            qdrant.qm.PointStruct(
                id=str(uuid.uuid4()),
                vector=vec,
                payload=payload,
            )
            for vec, payload in zip(vectors, payloads)
        ]

        result = client.upsert(collection_name="luna_chunks", points=points)
        logging.info(f"✅ Upsert abgeschlossen ({len(points)} Punkte). Ergebnis: {result.status}")
        console.info(f"✅ {len(points)} Vektoren erfolgreich in Qdrant upserted.")

    except Exception as e:
        logging.error(f"⚠️ Fehler beim Upsert in Qdrant: {e}")
        console.error(f"⚠️ Fehler beim Upsert in Qdrant: {e}")
        return

    # ---------------------------------------------------------
    # Versionierung
    # ---------------------------------------------------------
    version_path = MODEL_DIR / "last_retrain.txt"
    version_path.write_text(datetime.utcnow().isoformat() + "Z", encoding="utf-8")
    logging.info("Retraining erfolgreich abgeschlossen.")
    console.info("🏁 Retraining abgeschlossen.")

    elapsed = (datetime.utcnow() - start_time).total_seconds()
    logging.info(f"Gesamtdauer: {elapsed:.2f}s")


# -------------------------------------------------------------
# Main Entry
# -------------------------------------------------------------
if __name__ == "__main__":
    retrain_model()

