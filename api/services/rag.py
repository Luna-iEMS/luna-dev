import os, hashlib, yaml, traceback
from datetime import datetime
from . import embed, qdrant

# === Persona / System aus YAML laden ===
PROMPT_PATH = os.getenv("PROMPT_PATH", "prompts/luna.yml")
try:
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        conf = yaml.safe_load(f)
        PERSONA = conf.get("persona", "Du bist Luna, eine neutrale KI.")
        SYSTEM = conf.get("rag", {}).get("system", "")
except Exception:
    PERSONA = "Du bist Luna, eine neutrale KI."
    SYSTEM = ""

def _sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def chunk_text(text: str, max_len: int = 800):
    """Teilt längere Texte in handhabbare Chunks auf."""
    words, chunks, cur = text.split(), [], []
    for w in words:
        cur.append(w)
        if sum(len(x) + 1 for x in cur) >= max_len:
            chunks.append(" ".join(cur))
            cur = []
    if cur:
        chunks.append(" ".join(cur))
    return chunks


def ask(question: str, top_k: int = 6):
    """
    RAG-Anfrage:
    1. Frage einbetten → Qdrant-Suche
    2. Kontext kombinieren → Prompt generieren
    3. Antwort von LLM abrufen
    Immer strukturierte Ausgabe für API und Tests.
    """
    try:
        # === 1. Embedding ===
        q_emb = embed.embed_texts([question])[0]
        if not q_emb or not isinstance(q_emb, (list, tuple)):
            return {
                "answer": "Fehler: Kein gültiges Embedding erzeugt.",
                "status": "embedding_error",
                "chunks_used": [],
                "citations": []
            }

        # === 2. Qdrant-Suche ===
        hits = qdrant.search(q_emb, top_k=top_k)
        if not hits:
            return {
                "answer": "Keine passenden Quellen gefunden.",
                "status": "no_hits",
                "chunks_used": [],
                "citations": []
            }

        # === 3. Kontext zusammenbauen ===
        texts = [(h.payload.get("chunk_id"), h.payload.get("text", "")) for h in hits]
        context = "\n\n".join([f"[chunk {cid}] {txt}" for cid, txt in texts if txt])
        prompt = f"{SYSTEM}\n\nKontext:\n{context}\n\nFrage: {question}"

        # === 4. Antwort generieren ===
        answer = embed.generate(PERSONA, prompt)
        if not answer or not isinstance(answer, str):
            answer = "Keine Antwort generiert."

        # === 5. Strukturierte Rückgabe ===
        return {
            "answer": answer.strip(),
            "persona": PERSONA,
            "status": "ok",
            "chunks_used": [str(getattr(h, "id", "")) for h in hits],
            "citations": [
                {
                    "chunk_id": str(h.payload.get("chunk_id")),
                    "score": float(getattr(h, "score", 0.0))
                }
                for h in hits
            ],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except Exception as e:
        # Sauberes Fehlerobjekt für Smoke-Tests und API
        return {
            "answer": f"[Fehler in RAG.ask: {e}]",
            "trace": traceback.format_exc(),
            "status": "error",
            "chunks_used": [],
            "citations": []
        }
