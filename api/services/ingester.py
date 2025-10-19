# /app/services/ingester.py
from __future__ import annotations
import hashlib
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import requests
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue

# ---------- Konfiguration ----------
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "documents")
DOCS_DIR = os.getenv("LUNA_DOCS_DIR", "/data/docs-luna")  # compose mounten!

EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
EMBED_TIMEOUT = int(os.getenv("EMBED_TIMEOUT", "30"))

# ---------- Utilities ----------
def _md5(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def _read_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def _extract_title(md_text: str, fallback: str) -> str:
    for line in md_text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return fallback

def _simple_md_to_text(md: str) -> str:
    # sehr einfacher Fallback-„Parser“: Codeblöcke & Markup etwas ausdünnen
    import re
    txt = re.sub(r"```.*?```", " ", md, flags=re.S)
    txt = re.sub(r"`([^`]+)`", r"\1", txt)
    txt = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", txt)        # Bilder
    txt = re.sub(r"\[[^\]]+\]\(([^)]+)\)", r"\1", txt)     # Links -> URL
    txt = re.sub(r"[#>*_~]+", " ", txt)                    # Markdown-Symbole
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt

def _chunk(text: str, max_tokens: int = 512, overlap: int = 80) -> List[str]:
    # grobe Token-Approx über Wortanzahl
    words = text.split()
    if not words:
        return []
    approx_ratio = 0.75  # ~ 0.75 Wort ≈ 1 Token, grob
    chunk_size = max(50, int(max_tokens / approx_ratio))
    step = max(1, chunk_size - int(overlap / approx_ratio))
    chunks = []
    i = 0
    while i < len(words):
        piece = " ".join(words[i : i + chunk_size]).strip()
        if piece:
            chunks.append(piece)
        i += step
    return chunks

def _embed_batch(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []
    payload = {"model": EMBED_MODEL, "input": texts}
    r = requests.post(f"{OLLAMA_URL}/api/embed", json=payload, timeout=EMBED_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    # API liefert {"embeddings": [[...], ...]}
    return data.get("embeddings", [])

def _ensure_collection(client: QdrantClient, vector_size: Optional[int] = None):
    has = client.get_collections()
    names = {c.name for c in has.collections}
    if QDRANT_COLLECTION not in names:
        if vector_size is None:
            # „nomic-embed-text“ hat 768 Dimensionen (Stand heute).
            vector_size = 768
        client.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

# ---------- Public API ----------
def scan_and_ingest(
    base_dir: Optional[str | Path] = None,
    collection: Optional[str] = None,
    upsert: bool = True,
) -> Dict:
    base = Path(base_dir or DOCS_DIR)
    col = collection or QDRANT_COLLECTION
    if not base.exists():
        return {"status": "error", "message": f"Docs-Verzeichnis existiert nicht: {base}"}

    md_files = sorted([p for p in base.rglob("*.md") if p.is_file()])
    if not md_files:
        return {"status": "ok", "message": "Keine Markdown-Dateien gefunden.", "count_files": 0}

    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    _ensure_collection(client)

    total_points = 0
    ingested_files = 0
    errors: List[Tuple[str, str]] = []

    for path in md_files:
        try:
            raw = _read_markdown(path)
            title = _extract_title(raw, fallback=path.stem)
            text = _simple_md_to_text(raw)
            chunks = _chunk(text)
            if not chunks:
                continue

            embeds = _embed_batch(chunks)
            if not embeds:
                continue

            points: List[PointStruct] = []
            for idx, (chunk, vec) in enumerate(zip(chunks, embeds)):
                pid = int(_md5(f"{path}:{idx}")[:12], 16)  # stabile numerische ID
                payload = {
                    "source": str(path.relative_to(base)),
                    "title": title,
                    "text": chunk,
                    "file_hash": _md5(raw),
                    "chunk_index": idx,
                    "collection": col,
                }
                points.append(PointStruct(id=pid, vector=vec, payload=payload))

            client.upsert(collection_name=col, points=points)
            total_points += len(points)
            ingested_files += 1

        except Exception as e:
            errors.append((str(path), str(e)))

    # einfache Stats
    return {
        "status": "ok" if not errors else "partial",
        "collection": col,
        "docs_dir": str(base),
        "count_files": ingested_files,
        "count_points": total_points,
        "errors": [{"file": f, "error": err} for f, err in errors],
    }


def wipe_collection(collection: Optional[str] = None) -> Dict:
    """Löscht alle Daten aus der Collection (nicht die Collection selbst)."""
    col = collection or QDRANT_COLLECTION
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    # einfacher Weg: Punkte löschen via leeres Filter = alles
    client.delete(
        collection_name=col,
        points_selector=Filter(
            must=[FieldCondition(key="collection", match=MatchValue(value=col))]
        ),
    )
    return {"status": "ok", "collection": col, "message": "Alle Punkte gelöscht."}
