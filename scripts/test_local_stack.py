#!/usr/bin/env python3
"""
🌙 Luna IEMS – Lokaler Stack-Tester

Dieses Skript prüft automatisch:
1️⃣  API /health
2️⃣  Datei-Upload-Pipeline (/api/v1/ingest/upload)
3️⃣  RAG-Abfrage (/api/v1/rag/ask)

→ gibt farbige Statusmeldungen und eine Markdown-Zusammenfassung aus.
"""

import requests, json, os, sys, tempfile
from rich.console import Console
from rich.table import Table

API_BASE = os.getenv("API_URL", "http://localhost:8000")
console = Console()

def check_health():
    url = f"{API_BASE}/health"
    try:
        r = requests.get(url, timeout=10)
        if r.ok:
            console.print(f"✅ [green]API läuft:[/green] {r.json()}")
            return True
        else:
            console.print(f"❌ [red]Healthcheck fehlgeschlagen[/red]: {r.status_code}")
    except Exception as e:
        console.print(f"❌ [red]Health-Fehler:[/red] {e}")
    return False


def upload_test_file():
    url = f"{API_BASE}/api/v1/ingest/upload"
    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    tmpfile.write(b"Dies ist ein automatischer Integrationstest fuer Luna IEMS.\n")
    tmpfile.close()

    try:
        with open(tmpfile.name, "rb") as f:
            r = requests.post(url, files={"file": f}, timeout=60)
        if r.ok:
            console.print(f"✅ [green]Upload erfolgreich[/green]: {r.json()}")
            os.unlink(tmpfile.name)
            return True
        else:
            console.print(f"❌ [red]Upload fehlgeschlagen[/red]: {r.status_code} – {r.text}")
    except Exception as e:
        console.print(f"❌ [red]Upload-Fehler:[/red] {e}")
    return False


def rag_query():
    url = f"{API_BASE}/api/v1/rag/ask"
    payload = {"question": "Was steht in der Testdatei?"}
    try:
        r = requests.post(url, json=payload, timeout=90)
        if r.ok:
            data = r.json()
            answer = data.get("answer") or "(keine Antwort)"
            console.print(f"✅ [green]RAG-Abfrage erfolgreich[/green]: {answer[:100]}...")
            return True
        else:
            console.print(f"❌ [red]RAG-API-Fehler[/red]: {r.status_code} – {r.text}")
    except Exception as e:
        console.print(f"❌ [red]RAG-Request-Fehler:[/red] {e}")
    return False


def summary(results: dict):
    table = Table(title="Luna IEMS – Testzusammenfassung")
    table.add_column("Test", justify="left", style="cyan")
    table.add_column("Ergebnis", justify="center", style="green")
    for name, ok in results.items():
        table.add_row(name, "✅ OK" if ok else "❌ FAIL")
    console.print("\n")
    console.print(table)
    console.print("\n")
    ok_all = all(results.values())
    if ok_all:
        console.print("[bold green]🎯 Alle Tests erfolgreich! Luna IEMS-Stack ist stabil.[/bold green]")
    else:
        console.print("[bold red]❌ Einige Tests sind fehlgeschlagen. Logs prüfen![/bold red]")


def main():
    console.print("[bold cyan]\n🚀 Starte Luna IEMS Lokalt-Test...[/bold cyan]\n")
    results = {
        "Healthcheck": check_health(),
        "Upload-Test": upload_test_file(),
        "RAG-Abfrage": rag_query(),
    }
    summary(results)

if __name__ == "__main__":
    sys.exit(main())
