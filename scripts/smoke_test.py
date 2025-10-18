import requests, psycopg, os, sys
from rich.console import Console

console = Console()
API = "http://localhost:8000/api/v1"
DB_DSN = os.getenv("PG_DSN", "postgresql://postgres:postgres@localhost:5432/luna")

def ok(msg): console.print(f"✅ {msg}", style="green")
def warn(msg): console.print(f"⚠️ {msg}", style="yellow")
def fail(msg): console.print(f"❌ {msg}", style="red"); sys.exit(1)

def test_api():
    r = requests.get(f"{API}/system/info")
    r.raise_for_status()
    ok("API erreichbar")

def test_db():
    with psycopg.connect(DB_DSN) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM smart_meter_readings;")
        sm = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM market_prices;")
        mp = cur.fetchone()[0]
        if sm > 0 and mp > 0:
            ok("Simulation-Daten vorhanden")
        else:
            warn("Simulation noch leer")

def test_rag():
    q = {"question": "Was steht in sample.pdf?"}
    r = requests.post(f"{API}/rag/ask", json=q)
    if r.ok and "answer" in r.json():
        ok("RAG liefert Antwort")
    else:
        warn("RAG leer oder Fehler")

def test_recommend():
    r = requests.post(f"{API}/recommend", json={})
    if r.ok and r.json().get("items"):
        ok("Empfehlung aktiv")
    else:
        warn("Empfehlung leer")

def main():
    console.rule("[bold blue]Luna-IEMS Smoke-Test (Python)")
    try:
        test_api()
        test_db()
        test_rag()
        test_recommend()
        ok("Smoke-Test abgeschlossen")
    except Exception as e:
        fail(str(e))

if __name__ == "__main__":
    main()
