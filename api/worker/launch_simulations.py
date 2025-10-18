import threading
import time
import subprocess
import signal
import sys
from pathlib import Path
import os

# --- Robuste Pfad-Erkennung ---------------------------------------------

# Ermittle den absoluten Pfad zu diesem Skript
BASE_DIR = Path(__file__).resolve().parent

# Arbeite immer relativ zu diesem Verzeichnis
os.chdir(BASE_DIR)

# --- Zielskripte definieren ---------------------------------------------

# Nutze absolute Pfade, damit die Unterprozesse immer gefunden werden
TARGETS = [
    ("SmartMeter", ["python", "-u", str(BASE_DIR / "sim_smartmeter.py")]),
    ("Market", ["python", "-u", str(BASE_DIR / "sim_market.py")]),
]

processes = []


# --- Subprozesse starten ------------------------------------------------

def run_service(name, cmd):
    print(f"[launcher] starting {name} -> {' '.join(cmd)}", flush=True)
    proc = subprocess.Popen(cmd)
    processes.append(proc)
    proc.wait()


# --- Stop-Handler -------------------------------------------------------

def stop_all(signum=None, frame=None):
    print("\n[launcher] stopping all simulations...", flush=True)
    for p in processes:
        if p.poll() is None:
            p.terminate()
    sys.exit(0)


signal.signal(signal.SIGINT, stop_all)
signal.signal(signal.SIGTERM, stop_all)


# --- Hauptlogik ---------------------------------------------------------

def main():
    threads = []
    for name, cmd in TARGETS:
        t = threading.Thread(target=run_service, args=(name, cmd), daemon=True)
        t.start()
        threads.append(t)

    # Haupt-Loop: solange laufen, wie mindestens ein Thread aktiv ist
    try:
        while any(t.is_alive() for t in threads):
            time.sleep(1)
    except KeyboardInterrupt:
        stop_all()


if __name__ == "__main__":
    main()
