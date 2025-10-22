#!/usr/bin/env python3
"""
🔍 Luna IEMS – Ollama Model Setup & Update Tool
Prüft, ob benötigte Modelle installiert sind und aktualisiert sie bei Bedarf.
"""

import os
import requests
import subprocess
import time

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
REQUIRED_MODELS = ["llama3.1:8b", "nomic-embed-text"]

def run(cmd):
    """Hilfsfunktion zum sicheren Aufruf von Shell-Kommandos."""
    print(f"⚙️  {cmd}")
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def wait_for_ollama():
    """Wartet, bis der Ollama-Server erreichbar ist."""
    print("⏳ Warte auf Ollama-Server ...")
    for _ in range(20):
        try:
            r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=3)
            if r.status_code == 200:
                print("✅ Ollama-Server erreichbar.")
                return True
        except Exception:
            pass
        time.sleep(2)
    print("❌ Konnte Ollama nicht erreichen.")
    return False

def get_installed_models():
    """Liest die Liste der installierten Modelle."""
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        models = [m["name"] for m in r.json().get("models", [])]
        return models
    except Exception as e:
        print(f"⚠️ Fehler beim Abfragen der Modelle: {e}")
        return []

def ensure_models():
    """Installiert und aktualisiert die benötigten Modelle."""
    installed = get_installed_models()
    print(f"📦 Installierte Modelle: {installed}")

    for model in REQUIRED_MODELS:
        if model not in installed:
            print(f"⬇️ Lade fehlendes Modell: {model}")
            run(f"ollama pull {model}")
        else:
            print(f"🔁 Prüfe auf Updates für: {model}")
            run(f"ollama pull {model}")

if __name__ == "__main__":
    if wait_for_ollama():
        ensure_models()
        print("✅ Modelle geprüft und aktuell.")
    else:
        print("⚠️ Ollama nicht verfügbar – bitte Container prüfen.")
