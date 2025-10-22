#!/usr/bin/env python3
"""
🌙 Luna IEMS – Extended Smoke Test
Erzeugt automatisch einen Markdown-Report (artifacts/smoke_results.md).
Funktioniert sowohl im Host-System als auch im Docker-Container.
"""
import os, sys, time, requests, socket
from datetime import datetime, timezone
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()

# erkennen, ob im Container ausgeführt wird
IN_CONTAINER = Path("/.dockerenv").exists()
HOST_SUFFIX = "" if IN_CONTAINER else "localhost"
BASE_URL = f"http://{HOST_SUFFIX or 'localhost'}:8000"

def wait_for_api(max_wait: int = 10):
    """Wartet, bis FastAPI erreichbar ist, bevor Tests starten."""
    console.print("[grey]⏳ Warten auf API-Verfügbarkeit...[/grey]")
    for i in range(max_wait):
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=2)
            if r.ok:
                console.print(f"[green]✅ API erreichbar ({i+1}s)[/green]")
                return True
        except Exception:
            time.sleep(1)
    console.print("[red]❌ API nicht erreichbar.[/red]")
    return False

def check_http(name, url):
    """Einfacher HTTP-Check mit Timeout und Statusausgabe."""
    try:
        r = requests.get(url, timeout=8)
        return r.ok, f"{r.status_code} → {url}"
    except Exception as e:
        return False, str(e)

def main():
    console.print("\n[bold cyan]🔍 Luna IEMS – Smoke Test[/bold cyan]")

    if not wait_for_api(15):
        console.print("[red]Abbruch: API nicht verfügbar.[/red]")
        sys.exit(1)

    # Container-interne vs. externe Hosts
    if IN_CONTAINER:
        qdrant_host, tika_host, ollama_host = "qdrant", "tika", "ollama"
    else:
        qdrant_host = tika_host = ollama_host = "localhost"

    checks = {
        "FastAPI /health": f"{BASE_URL}/health",
        "System Info": f"{BASE_URL}/api/v1/system/info",
        "Qdrant": f"http://{qdrant_host}:6333/readyz",
        "Tika": f"http://{tika_host}:9998/tika",
        "Ollama": f"http://{ollama_host}:11434/api/tags",
    }

    results = {k: check_http(k, v) for k, v in checks.items()}

    # --- RAG /ask-Test ---
    try:
        payload = {"question": "Was ist das Luna IEMS?", "top_k": 2}
        r = requests.post(f"{BASE_URL}/api/v1/rag/ask", json=payload, timeout=25)
        if not r.ok:
            results["RAG /ask"] = (False, f"HTTP {r.status_code}")
        else:
            data = r.json()
            answer = (
                data.get("data", {}).get("answer")
                if isinstance(data.get("data"), dict)
                else None
            )
            if answer and len(answer.strip()) > 0:
                short = (answer[:120] + "...") if len(answer) > 120 else answer
                results["RAG /ask"] = (True, f"Antwort erhalten: {short}")
            else:
                results["RAG /ask"] = (False, "Antwort leer oder kein 'data.answer' vorhanden")
    except Exception as e:
        results["RAG /ask"] = (False, str(e))

    ok_all = all(v[0] for v in results.values())

    # Konsolen-Tabelle
    table = Table(title="Smoke Test Results")
    table.add_column("Service", justify="left")
    table.add_column("Status", justify="center")
    table.add_column("Detail", justify="left")
    for k, (ok, detail) in results.items():
        symbol = "✅ OK" if ok else "❌ FAIL"
        table.add_row(k, symbol, detail)
    console.print(table)

    # Markdown-Report
    p = Path("artifacts")
    p.mkdir(exist_ok=True, parents=True)
    f = p / "smoke_results.md"

    with f.open("w", encoding="utf-8") as out:
        out.write("# 🧪 Luna IEMS Smoke Test Report\n")
        out.write(f"**Date:** {datetime.now(timezone.utc).isoformat()} UTC\n\n")
        out.write("| Service | Status | Detail |\n|---|---|---|\n")
        for k, (ok, d) in results.items():
            out.write(f"| {k} | {'✅ OK' if ok else '❌ FAIL'} | {d} |\n")
        out.write("\n" + ("✅ Alle Services stabil.\n" if ok_all else "❌ Fehler aufgetreten.\n"))

    console.print(f"\n📄 Markdown-Report → {f}")
    sys.exit(0 if ok_all else 1)

if __name__ == "__main__":
    main()


