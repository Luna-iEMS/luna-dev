from . import embed, qdrant
from datetime import datetime
import hashlib

PERSONA = "Du bist Luna, Expertin für Energie- und Marktmanagement. Antworte präzise und zitiere [chunk <ID>]."

def _sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def chunk_text(text: str, max_len: int = 800):
    words, chunks, cur = text.split(), [], []
    for w in words:
        cur.append(w)
        if sum(len(x)+1 for x in cur) >= max_len:
            chunks.append(" ".join(cur))
            cur = []
    if cur:
        chunks.append(" ".join(cur))
    return chunks

def ask(question: str, top_k: int = 6):
    # Simplified: this function assumes an index exists already.
    # In a full impl, you'd embed the question, then search Qdrant.
    q_emb = embed.embed_texts([question])[0]
    hits = qdrant.search(q_emb, top_k=top_k)
    ids = [h.id for h in hits]
    texts = [(h.payload.get("chunk_id"), h.payload.get("text", "")) for h in hits]
    context = "\n\n".join([f"[chunk {cid}] {txt}" for cid, txt in texts])
    prompt = f"{PERSONA}\n\nKontext:\n{context}\n\nFrage: {question}"
    answer = embed.generate(PERSONA, prompt)
    return {"answer": answer, "chunks_used": ids, "citations": [
        {"chunk_id": str(h.payload.get("chunk_id")), "score": float(h.score)} for h in hits
    ]}
