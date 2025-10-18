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

DB_DSN = os.getenv("PG_DSN", "postgresql://postgres:postgres@db:5432/luna")
INTERVAL = int(os.getenv("SIM_MARKET_INTERVAL_SEC", "300"))
MARKETS = os.getenv("SIM_MARKETS", "EEX,APX").split(",")
PRODUCTS = os.getenv("SIM_PRODUCTS", "BASE,PEAK").split(",")
OUTPUT_DIR = Path(os.getenv("SIM_OUTPUT", "/data/sim/market"))
USE_MINIO = os.getenv("SIM_USE_MINIO", "false").lower() == "true"

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "sim")

def ensure_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS market_prices (
            market TEXT NOT NULL,
            product TEXT NOT NULL,
            ts TIMESTAMPTZ NOT NULL,
            price_eur_mwh DOUBLE PRECISION,
            volume DOUBLE PRECISION,
            PRIMARY KEY (market, product, ts)
        );
        """)
    conn.commit()

def generate_record(market, product):
    return (
        market,
        product,
        datetime.now(timezone.utc),
        round(random.uniform(30, 200), 2),
        round(random.uniform(10, 500), 2),
    )

def write_db(conn, records):
    with conn.cursor() as cur:
        cur.executemany("""
            INSERT INTO market_prices (market, product, ts, price_eur_mwh, volume)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, records)
    conn.commit()

def write_csv(records):
    folder = OUTPUT_DIR / datetime.utcnow().strftime("%Y/%m/%d")
    folder.mkdir(parents=True, exist_ok=True)
    fpath = folder / "market_prices.csv"
    newfile = not fpath.exists()
    with open(fpath, "a", encoding="utf-8") as f:
        if newfile:
            f.write("market,product,ts,price_eur_mwh,volume\n")
        for r in records:
            f.write(f"{r[0]},{r[1]},{r[2].isoformat()},{r[3]},{r[4]}\n")
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

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[sim_market] connected to {DB_DSN}, interval={INTERVAL}s", flush=True)
    with psycopg.connect(DB_DSN) as conn:
        ensure_table(conn)
        while RUNNING:
            rows = [generate_record(m, p) for m in MARKETS for p in PRODUCTS]
            write_db(conn, rows)
            local_file = write_csv(rows)
            upload_minio(local_file)
            print(f"[sim_market] inserted {len(rows)} rows", flush=True)
            time.sleep(INTERVAL)
    print("[sim_market] stopped gracefully.", flush=True)

if __name__ == "__main__":
    main()
