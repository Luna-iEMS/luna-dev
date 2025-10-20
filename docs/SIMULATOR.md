# SIMULATOR — Smart‑Meter & Marktpreise

## Ziel
Simulation realer Energie‑ und Marktumgebungen für Entwicklung, Tests und Demos.

## Module
- `smart_meter_sim.py`: erzeugt Verbrauch/Produktion (zeitreihenartig, noise‑modelliert)
- `market_price_sim.py`: erzeugt Marktpreise (Day‑Ahead, Intraday) mit Volatilitäts‑Logik

## API
Beide Simulatoren liefern Timescale‑kompatible Zeitreihen:
```json
{ "ts": "...", "consumption_kw": 10.2, "production_kw": 3.1, "price_eur_mwh": 62.3 }
```

## Erweiterung
Später werden reale Adapter (Netzbetreiber, EPEX) angeschlossen.
