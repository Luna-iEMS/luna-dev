import requests, os
TIKA_URL = f"http://luna_tika:{os.getenv('TIKA_PORT','9998')}/tika"
HEADERS = {"Accept": "text/plain"}
def extract_text(file_bytes: bytes, filename: str) -> str:
    r = requests.put(TIKA_URL, headers=HEADERS, data=file_bytes, timeout=60)
    r.raise_for_status()
    return r.text
