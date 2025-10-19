"""
Luna IEMS – Recommender Service (M4)
Content-basierte Empfehlungen + Feedback-Speicherung
"""

import psycopg
from typing import List, Dict, Any
from services.db import conn


# -------------------------------------------------------------
# 📊 Datenquellen abrufen
# -------------------------------------------------------------
def get_recent_data(hours: int = 24) -> Dict[str, list]:
    """Liest aktuelle Smart-Meter- und Marktpreise aus der DB"""
    with conn() as c, c.cursor() as cur:
        cur.execute("""
            SELECT meter_id, ts, consumption_kw, production_kw, voltage
            FROM smart_meter_readings
            WHERE ts > NOW() - INTERVAL '%s hour'
            ORDER BY ts DESC;
        """, (hours,))
        meter = cur.fetchall()

        cur.execute("""
            SELECT market, product, ts, price_eur_mwh, volume
            FROM market_prices
            WHERE ts > NOW() - INTERVAL '%s hour'
            ORDER BY ts DESC;
        """, (hours,))
        market = cur.fetchall()

    return {"meter": meter, "market": market}


# -------------------------------------------------------------
# 🧠 Empfehlungen generieren
# -------------------------------------------------------------
def recommend_from_data(hours: int = 24) -> List[Dict[str, Any]]:
    """Einfache content-basierte Empfehlungen"""
    data = get_recent_data(hours=hours)
    meter = data.get("meter", [])
    market = data.get("market", [])

    if not meter or not market:
        return [{"type": "info", "text": "Noch keine Daten verfügbar – Simulation läuft."}]

    avg_consumption = sum(r[2] for r in meter) / len(meter)
    avg_price = sum(r[3] for r in market) / len(market)

    recs = []
    if avg_consumption > 2.0 and avg_price < 90:
        recs.append({
            "type": "price_opportunity",
            "text": f"Hoher Verbrauch erkannt, aber Marktpreis günstig ({avg_price:.1f} €/MWh). Nutzung in dieser Phase lohnt sich!"
        })
    elif avg_price > 150:
        recs.append({
            "type": "saving_tip",
            "text": f"Marktpreise sind aktuell hoch ({avg_price:.1f} €/MWh). Vermeide Spitzenverbrauch in den nächsten Stunden."
        })
    else:
        recs.append({
            "type": "neutral",
            "text": f"Verbrauch und Marktpreise stabil ({avg_price:.1f} €/MWh). Keine Maßnahmen nötig."
        })

    return recs


# -------------------------------------------------------------
# 💬 Feedback-System
# -------------------------------------------------------------
def ensure_feedback_table():
    with conn() as c, c.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS recommend_feedback (
            id SERIAL PRIMARY KEY,
            ts TIMESTAMPTZ DEFAULT NOW(),
            user_id TEXT,
            recommendation_type TEXT,
            rating INTEGER CHECK (rating BETWEEN 1 AND 5),
            comment TEXT
        );
        """)
        c.commit()


def store_feedback(user_id: str, recommendation_type: str, rating: int, comment: str = None):
    ensure_feedback_table()
    with conn() as c, c.cursor() as cur:
        cur.execute("""
            INSERT INTO recommend_feedback (user_id, recommendation_type, rating, comment)
            VALUES (%s, %s, %s, %s);
        """, (user_id, recommendation_type, rating, comment))
        c.commit()


def get_feedback_stats():
    ensure_feedback_table()
    with conn() as c, c.cursor() as cur:
        cur.execute("""
            SELECT recommendation_type, COUNT(*), AVG(rating)
            FROM recommend_feedback
            GROUP BY recommendation_type
            ORDER BY COUNT(*) DESC;
        """)
        rows = cur.fetchall()
    return [
        {"type": r[0], "count": r[1], "avg_rating": round(r[2], 2)} for r in rows
    ]
