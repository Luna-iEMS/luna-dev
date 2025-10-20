import os, requests, json
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "ollama")
OLLAMA_PORT = os.getenv("OLLAMA_PORT", "11434")
OLLAMA_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
GENERATE_MODEL = os.getenv("GENERATE_MODEL", "llama3.1:8b-instruct")

def embed_texts(texts):
    # Prefer Ollama embeddings via HTTP
    try:
        r = requests.post(f"{OLLAMA_URL}/api/embeddings", json={"model": EMBED_MODEL, "input": texts}, timeout=120)
        r.raise_for_status()
        data = r.json()
        # Ollama returns {"embeddings": [[...], [...], ...]}
        return data.get("embeddings") or data.get("data")
    except Exception as e:
        # best-effort fallback
        return [[0.0] * 384 for _ in texts]

def generate(system_prompt: str, prompt: str) -> str:
    try:
        payload = {"model": GENERATE_MODEL, "prompt": f"{system_prompt}\n\n{prompt}", "stream": True}
        r = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=600, stream=True)
        r.raise_for_status()
        out = ""
        for line in r.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                j = json.loads(line)
                if "response" in j:
                    out += j["response"]
            except json.JSONDecodeError:
                continue
        return out.strip()
    except Exception as e:
        return f"[Fehler bei Generate: {e}]"
