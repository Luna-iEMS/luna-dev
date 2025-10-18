from fastapi import APIRouter, Query
from typing import Optional
import os, psycopg

router = APIRouter(prefix="/api/v1/data", tags=["data"])

DB_CONN = {
    "host": os.getenv("DB_HOST", "luna_db"),
    "port": os.getenv("DB_PORT", "5432"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASS", "postgres"),
    "dbname": os.getenv("DB_NAME", "postgres"),
}

@router.get("/market")
def get_market(
    market: Optional[str] = Query(None),
    product: Optional[str] = Query(None),
    from_ts: Optional[str] = Query(None),
    to_ts: Optional[str] = Query(None),
    limit: int = Query(100)
):
    sql = "SELECT market, product, ts, price_eur_mwh, volume FROM market_prices WHERE 1=1"
    params = {}
    if market:
        sql += " AND market = %(market)s"
        params["market"] = market
    if product:
        sql += " AND product = %(product)s"
        params["product"] = product
    if from_ts:
        sql += " AND ts >= %(from_ts)s"
        params["from_ts"] = from_ts
    if to_ts:
        sql += " AND ts <= %(to_ts)s"
        params["to_ts"] = to_ts
    sql += " ORDER BY ts DESC LIMIT %(limit)s"
    params["limit"] = limit

    with psycopg.connect(**DB_CONN) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    cols = ["market", "product", "ts", "price_eur_mwh", "volume"]
    data = [dict(zip(cols, r)) for r in rows]
    return {"status": "ok", "count": len(data), "data": data}
