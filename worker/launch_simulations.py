import threading
import time
import subprocess
import signal
import sys

# Services, die parallel laufen sollen
TARGETS = [
    ("SmartMeter", ["python", "-u", "sim_smartmeter.py"]),
    ("Market", ["python", "-u", "sim_market.py"]),
]

processes = []

def run_service(name, cmd):
    print(f"[launcher] starting {name} -> {' '.join(cmd)}", flush=True)
    proc = subprocess.Popen(cmd)
    processes.append(proc)
    proc.wait()

def stop_all(signum=None, frame=None):
    print("\n[launcher] stopping all simulations...", flush=True)
    for p in processes:
        if p.poll() is None:
            p.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, stop_all)
signal.signal(signal.SIGTERM, stop_all)

def main():
    threads = []
    for name, cmd in TARGETS:
        t = threading.Thread(target=run_service, args=(name, cmd), daemon=True)
        t.start()
        threads.append(t)

    # Warten, bis beide Threads beendet sind
    try:
        while any(t.is_alive() for t in threads):
            time.sleep(1)
    except KeyboardInterrupt:
        stop_all()

if __name__ == "__main__":
    main()
