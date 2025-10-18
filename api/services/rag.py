from . import embed, qdrant, db
from datetime import datetime
import json, hashlib, logging

PERSONA = """Du bist Luna, eine Expertin für Energie- und Marktmanagement.
Antworte präzise, sachlich und beziehe dich auf relevante Textstellen.
Füge in eckigen Klammern die Chunk-IDs an, z. B. [chunk 5]."""

# Hilfsfunktionen
def _sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def chunk_text(text: str, max_len: int = 800):
    """Zerteilt Text in semantische Blöcke."""
    words, chunks, cur = text.split(), [], []
    for w in words:
        cur.append(w)
        if sum(len(x) + 1 for x in cur) > max_len:
            chunks.append(" ".join(cur))
            cur = []
    if cur:
        chunks.append(" ".join(cur))
    return [{"idx": i, "text": c} for i, c in enumerate(chunks)]

def ingest_bytes(file_bytes: bytes, title: str, kind="document", source="upload", tags=None):
    tags = tags or []
    sha = _sha256(file_bytes)
    with db.conn() as c, c.cursor() as cur:
        cur.execute("SELECT item_id FROM items WHERE sha256=%s", (sha,))
        row = cur.fetchone()
        if row:
            item_id = row[0]
        else:
            cur.execute(
                """INSERT INTO items(kind, source, title, tags, sha256, created_at)
                   VALUES(%s, %s, %s, %s, %s, NOW())
                   RETURNING item_id""",
                (kind, source, title, tags, sha),
            )
            item_id = cur.fetchone()[0]
        c.commit()
    return item_id, sha

def index_chunks(item_id: str, chunks: list[dict]):
    texts = [c["text"] for c in chunks]
    vecs = embed.embed_texts(texts)
    dim = len(vecs[0]) if vecs else 0
    qdrant.ensure_collection(dim)
    ids, payloads = [], []
    with db.conn() as c, c.cursor() as cur:
        for cdef, vec in zip(chunks, vecs):
            cur.execute(
                """INSERT INTO item_chunks(item_id, chunk_idx, text, metadata)
                   VALUES(%s,%s,%s,%s)
                   RETURNING chunk_id""",
                (item_id, cdef["idx"], cdef["text"], json.dumps({})),
            )
            cid = cur.fetchone()[0]
            ids.append(str(cid))
            payloads.append({
                "chunk_id": str(cid),
                "item_id": str(item_id),
                "title": f"Item {item_id}",
                "timestamp": datetime.now().isoformat(),
            })
        c.commit()
    qdrant.upsert_vectors(ids, vecs, payloads)
    return len(ids)

def ask(question: str, top_k: int = 6, min_score: float = 0.25):
    """Führt semantische Suche + Antwortgenerierung durch."""
    q_vec = embed.embed_texts([question])[0]
    hits = qdrant.search(q_vec, top_k=top_k)
    # Relevante Treffer filtern
    hits = [h for h in hits if float(h.score) >= min_score]
    ids = [h.payload.get("chunk_id") for h in hits if h.payload]
    texts = []
    if ids:
        with db.conn() as c, c.cursor() as cur:
            cur.execute(
                "SELECT chunk_id, text FROM item_chunks WHERE chunk_id = ANY(%s)",
                (ids,),
            )
            for cid, txt in cur.fetchall():
                texts.append((str(cid), txt))
    context = "\n\n".join([f"[chunk {cid}] {txt}" for cid, txt in texts])
    prompt = f"{PERSONA}\n\nKontext:\n{context}\n\nFrage: {question}"
    try:
        answer = embed.generate(PERSONA, prompt)
    except Exception as e:
        answer = f"[Fehler bei Generate: {e}]"
    return {
        "answer": answer,
        "chunks_used": ids,
        "citations": [
            {"chunk_id": str(h.payload.get("chunk_id")), "score": float(h.score)}
            for h in hits
        ],
    }
