import os
import time
import random
import signal
from datetime import datetime, timezone
from pathlib import Path
import psycopg

try:
    from minio import Minio
except Exception:
    Minio = None

RUNNING = True

def stop_handler(signum, frame):
    global RUNNING
    RUNNING = False

signal.signal(signal.SIGTERM, stop_handler)
signal.signal(signal.SIGINT, stop_handler)

# --- ENV / Defaults ----------------------------------------------------------

DB_DSN = os.getenv("PG_DSN", "postgresql://postgres:postgres@db:5432/luna")
INTERVAL = int(os.getenv("SIM_SMARTMETER_INTERVAL_SEC", "60"))
METERS = [m.strip() for m in os.getenv("SIM_METERS", "MTR-1,MTR-2").split(",") if m.strip()]
OUTPUT_DIR = Path(os.getenv("SIM_OUTPUT", "/data/sim/smartmeter"))
USE_MINIO = os.getenv("SIM_USE_MINIO", "false").lower() == "true"

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "sim")

# --- DB Schema Setup ---------------------------------------------------------

def ensure_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS smart_meter_readings (
            meter_id TEXT NOT NULL,
            ts TIMESTAMPTZ NOT NULL,
            consumption_kw DOUBLE PRECISION,
            production_kw DOUBLE PRECISION,
            voltage DOUBLE PRECISION,
            quality TEXT,
            PRIMARY KEY (meter_id, ts)
        );
        """)
    conn.commit()

# --- Data Generation ---------------------------------------------------------

def generate_reading(meter_id: str):
    ts = datetime.now(timezone.utc)
    consumption = round(random.uniform(0.2, 5.5), 3)
    production = round(random.uniform(0.0, 3.5), 3)
    voltage = round(random.uniform(220.0, 240.0), 2)
    quality = "ok"
    return (meter_id, ts, consumption, production, voltage, quality)

def write_db(conn, records):
    with conn.cursor() as cur:
        cur.executemany("""
            INSERT INTO smart_meter_readings
            (meter_id, ts, consumption_kw, production_kw, voltage, quality)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (meter_id, ts) DO NOTHING;
        """, records)
    conn.commit()

def write_csv(records):
    folder = OUTPUT_DIR / datetime.utcnow().strftime("%Y/%m/%d")
    folder.mkdir(parents=True, exist_ok=True)
    fpath = folder / "smart_meter_readings.csv"
    newfile = not fpath.exists()
    with open(fpath, "a", encoding="utf-8") as f:
        if newfile:
            f.write("meter_id,ts,consumption_kw,production_kw,voltage,quality\n")
        for r in records:
            f.write(f"{r[0]},{r[1].isoformat()},{r[2]},{r[3]},{r[4]},{r[5]}\n")
    return fpath

def upload_minio(local_file: Path):
    if not USE_MINIO or Minio is None:
        return
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )
    if not client.bucket_exists(MINIO_BUCKET):
        client.make_bucket(MINIO_BUCKET)
    object_key = str(local_file.relative_to(OUTPUT_DIR))
    client.fput_object(MINIO_BUCKET, object_key, str(local_file))

# --- Main Loop ---------------------------------------------------------------

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[sim_smartmeter] connected to {DB_DSN}, meters={METERS}, interval={INTERVAL}s", flush=True)
    with psycopg.connect(DB_DSN) as conn:
        ensure_table(conn)
        while RUNNING:
            rows = [generate_reading(m) for m in METERS]
            write_db(conn, rows)
            local_file = write_csv(rows)
            upload_minio(local_file)
            print(f"[sim_smartmeter] inserted {len(rows)} readings", flush=True)
            time.sleep(INTERVAL)
    print("[sim_smartmeter] stopped gracefully.", flush=True)

if __name__ == "__main__":
    main()
