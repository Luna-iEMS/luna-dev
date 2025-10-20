import os, logging
from pathlib import Path
from api.services import embed, qdrant

DATA_DIR = Path(os.getenv("DATA_DIR", "/data/incoming"))
MODEL_DIR = Path(os.getenv("MODEL_DIR", "/models/versions"))
LOG_FILE = Path(os.getenv("LOG_FILE", "/logs/train_pipeline.log"))

MODEL_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(filename=str(LOG_FILE), level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")

def discover_texts():
    files = []
    for p in DATA_DIR.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".txt", ".md"}:
            files.append(p)
    return files

def retrain_model():
    files = discover_texts()
    if not files:
        logging.info("Keine neuen Daten gefunden.")
        return

    vectors, payloads, ids = [], [], []
    for idx, path in enumerate(files):
        text = path.read_text(encoding="utf-8", errors="ignore")
        emb = embed.embed_texts([text])[0]
        vectors.append(emb)
        payloads.append({"path": str(path), "chunk_id": idx, "text": text[:1000]})
        ids.append(idx)

    qdrant.ensure_collection(dim=len(vectors[0]) if vectors else 768)
    qdrant.upsert_vectors(ids, vectors, payloads)

    version_path = MODEL_DIR / "last_retrain.txt"
    version_path.write_text("ok", encoding="utf-8")
    logging.info("Retraining erfolgreich abgeschlossen.")

if __name__ == "__main__":
    retrain_model()
