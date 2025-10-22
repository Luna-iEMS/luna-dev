import os
import time
import threading
import subprocess
import requests
from pathlib import Path
from api.services import qdrant

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
QDRANT_HOST = os.getenv("QDRANT_HOST", "http://qdrant:6333")
CACHE_DIR = Path(os.getenv("CACHE_DIR", "/tmp/luna-cache"))
REQUIRED_MODELS = ["llama3.1:8b", "nomic-embed-text"]

CACHE_DIR.mkdir(parents=True, exist_ok=True)
print(f"🧩 Cache aktiviert unter: {CACHE_DIR}")

def run(cmd: str):
    subprocess.run(cmd, shell=True, check=False)

def wait_for_service(url: str, name: str, timeout: int = 30):
    print(f"⏳ Warte auf {name} ({url}) – bis zu {timeout}s …")
    start = time.time()
    while True:
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                print(f"✅ {name} erreichbar.")
                return True
        except Exception:
            pass
        if time.time() - start > timeout:
            print(f"⚠️ {name} nicht erreichbar nach {timeout}s – fahre fort.")
            return False
        time.sleep(2)

def ensure_ollama():
    if not wait_for_service(f"{OLLAMA_HOST}/api/tags", "Ollama", timeout=30):
        print("⚠️ Ollama nicht erreichbar – überspringe Modell-Setup.")
        return
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags").json()
        installed = [m["name"] for m in response.get("models", [])]
        for model in REQUIRED_MODELS:
            if model not in installed:
                print(f"⬇️ Lade Modell {model} …")
                run(f"ollama pull {model}")
            else:
                print(f"🔁 Prüfe Updates für {model} …")
                run(f"ollama pull {model}")
        print("🧠 Modelle geladen.")
    except Exception as e:
        print(f"⚠️ Fehler bei Ollama-Setup: {e}")

def ensure_qdrant():
    """Überprüft und initialisiert Qdrant-Collection."""
    # neuer robuster Check
    if not wait_for_service(f"{QDRANT_HOST}/healthz", "Qdrant", timeout=40):
        if not wait_for_service(f"{QDRANT_HOST}/health", "Qdrant", timeout=10):
            print("⚠️ Qdrant nicht erreichbar – überspringe Collection-Setup.")
            return
    try:
        qdrant.ensure_collection(dim=384)
        print("✅ Qdrant Collection 'luna_chunks' vorhanden.")
    except Exception as e:
        print(f"⚠️ Qdrant Setup-Fehler: {e}")

def ensure_dirs():
    for p in ["/data/incoming", "/logs", "/models/versions"]:
        Path(p).mkdir(parents=True, exist_ok=True)
        print(f"📁 {p} vorhanden.")

def startup():
    print("🚀 Starte Luna IEMS – High Performance Mode …")
    ensure_dirs()
    t1 = threading.Thread(target=ensure_ollama, daemon=True)
    t2 = threading.Thread(target=ensure_qdrant, daemon=True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print("🌙 Luna IEMS Startup abgeschlossen.")
    print("──────────────────────────────────────")
    print(f"🧠 OLLAMA : {OLLAMA_HOST}")
    print(f"📡 QDRANT : {QDRANT_HOST}")
    print(f"🧩 Modelle: {', '.join(REQUIRED_MODELS)}")
    print("──────────────────────────────────────")

if __name__ == "__main__":
    startup()


