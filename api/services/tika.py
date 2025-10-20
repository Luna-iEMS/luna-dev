import os, requests
TIKA_HOST = os.getenv("TIKA_HOST", "tika")
TIKA_PORT = os.getenv("TIKA_PORT", "9998")
TIKA_URL = f"http://{TIKA_HOST}:{TIKA_PORT}/tika"
HEADERS = {"Accept": "text/plain"}

def extract_text(file_bytes: bytes, filename: str) -> str:
    r = requests.put(TIKA_URL, headers=HEADERS, data=file_bytes, timeout=60)
    r.raise_for_status()
    return r.text
