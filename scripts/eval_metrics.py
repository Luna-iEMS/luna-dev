"""
🌙 Luna IEMS – Mini-Eval (Hit@K, MRR Placeholder)
Lädt einfache Fragen aus einer optionalen Datei /data/eval/questions.json und misst Antwortlatenz.
Struktur:
[{"q": "Frage 1"}, {"q": "Frage 2"}]
"""
import time, json, os, requests
from statistics import mean

BASE_URL = os.getenv("API_BASE", "http://localhost:8000")

def load_questions():
    path = "/data/eval/questions.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    # Fallback
    return [{"q":"Was ist das Luna IEMS?"}]

def main():
    qs = load_questions()
    lats = []
    for item in qs:
        q = item["q"]
        t0 = time.time()
        r = requests.post(f"{BASE_URL}/api/v1/rag/ask", json={"question": q, "top_k": 4}, timeout=30)
        dt = time.time() - t0
        lats.append(dt)
        if r.ok:
            j = r.json()
            print(f"Q: {q}\n→ {j.get('data',{}).get('answer','<no answer>')[:120]}...\nlat={dt:.2f}s\n")
        else:
            print(f"Q: {q}\nHTTP {r.status_code}\n")

    print(f"⏱️ Decision-Latency (avg): {mean(lats):.2f}s over {len(lats)} queries")

if __name__ == "__main__":
    main()
