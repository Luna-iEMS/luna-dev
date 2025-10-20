import os, psycopg
def conn():
    return psycopg.connect(
        host=os.getenv("DB_HOST","db"),
        port=os.getenv("DB_PORT","5432"),
        user=os.getenv("DB_USER","postgres"),
        password=os.getenv("DB_PASSWORD") or os.getenv("DB_PASS","postgres"),
        dbname=os.getenv("DB_NAME","luna")
    )
