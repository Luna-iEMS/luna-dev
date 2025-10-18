
import os
import requests
import json

# === Grundkonfiguration ===
OLLAMA_URL = f"http://luna_ollama:{os.getenv('OLLAMA_PORT', '11434')}"
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
GEN_MODEL = os.getenv("GENERATE_MODEL", "llama3:8b-instruct-q4_K_M")

# === Embedding-Funktion ===
try:
    from sentence_transformers import SentenceTransformer
    _local_model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_texts(texts):
        if not texts:
            return []
        return _local_model.encode(texts, convert_to_numpy=True).tolist()

except Exception:
    def embed_texts(texts):
        if not texts:
            return []
        r = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBED_MODEL, "input": texts},
            timeout=60
        )
        r.raise_for_status()
        j = r.json()
        if "embedding" in j:
            return [j["embedding"]]
        if "embeddings" in j:
            return [e["embedding"] for e in j["embeddings"]]
        raise ValueError(f"Unexpected embedding format: {j}")

# === Textgenerierung (für Antworten) ===
def generate(system_prompt: str, user_prompt: str) -> str:
    """Ruft Ollama auf, um eine Antwort zu generieren."""
    prompt = f"{system_prompt.strip()}\n\n{user_prompt.strip()}"
    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": GEN_MODEL, "prompt": prompt},
            stream=True,
            timeout=120,
        )
        r.raise_for_status()

        text = ""
        for line in r.iter_lines(decode_unicode=True):
            if not line.strip():
                continue
            try:
                j = json.loads(line)
                if "response" in j:
                    text += j["response"]
            except json.JSONDecodeError:
                # Falls Ollama mal was Unerwartetes streamt
                continue
        return text.strip() or "[Keine Antwort von Ollama erhalten]"
    except Exception as e:
        return f"[Fehler bei Ollama-Generate: {e}]"
