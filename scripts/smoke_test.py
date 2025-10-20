#!/usr/bin/env python3
"""
🌙 Luna IEMS – Extended Smoke Test
Erzeugt automatisch einen Markdown-Report (artifacts/smoke_results.md).
"""

import sys, requests
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()
BASE_URL = "http://localhost:8000"

def check_http(name, url):
    try:
        r = requests.get(url, timeout=5)
        return r.ok, f"{r.status_code} → {url}"
    except Exception as e:
        return False, str(e)

def main():
    console.print("\n[bold cyan]🔍 Luna IEMS – Smoke Test[/bold cyan]")
    checks = {
        "FastAPI /health": f"{BASE_URL}/health",
        "System Info": f"{BASE_URL}/api/v1/system/info",
        "Qdrant": "http://localhost:6333/readyz",
        "Tika": "http://localhost:9998/tika",
        "Ollama": "http://localhost:11434/api/tags",
    }

    results = {k: check_http(k, v) for k, v in checks.items()}
    ok_all = all(v[0] for v in results.values())

    # Konsolen-Tabelle
    table = Table(title="Smoke Test Results")
    table.add_column("Service"); table.add_column("Status"); table.add_column("Detail")
    for k, (ok, detail) in results.items():
        table.add_row(k, "✅ OK" if ok else "❌ FAIL", detail)
    console.print(table)

    # Markdown-Report
    p = Path("artifacts"); p.mkdir(exist_ok=True)
    f = p / "smoke_results.md"
    with f.open("w", encoding="utf-8") as out:
        out.write(f"# 🧪 Luna IEMS Smoke Test Report\n")
        out.write(f"**Date:** {datetime.utcnow().isoformat()} UTC\n\n")
        out.write("| Service | Status | Detail |\n|---|---|---|\n")
        for k, (ok, d) in results.items():
            out.write(f"| {k} | {'✅ OK' if ok else '❌ FAIL'} | {d} |\n")
        out.write("\n" + ("✅ Alle Services stabil.\n" if ok_all else "❌ Fehler aufgetreten.\n"))
    console.print(f"\n📄 Markdown-Report → {f}")
    sys.exit(0 if ok_all else 1)

if __name__ == "__main__":
    main()
