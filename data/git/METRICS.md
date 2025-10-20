# METRICS — Luna‑IEMS Lern‑ & Empfehlungsmetriken
Stand: 2025-10-20

## Überblick
Diese Metriken bilden Luna’s antifragile Lernlogik ab — von Retrieval bis Wirkung.

### 1. Retrieval‑Qualität
| Metrik | Beschreibung | Quelle |
|--------|---------------|--------|
| **Hit@K** | Anteil relevanter Chunks in Top‑K | Eval‑Set |
| **MRR** | Mean Reciprocal Rank (1/Position der ersten korrekten Quelle) | Eval‑Set |
| **Context‑Precision** | relevante Tokens / Gesamtcontext | RAG Logs |

### 2. Empfehlungsleistung
| Metrik | Beschreibung | Quelle |
|--------|---------------|--------|
| **CTR (Click‑Through‑Rate)** | Anteil geöffneter Empfehlungen | events |
| **Useful‑Rate** | Anteil Feedbacks mit `useful=True` | feedback_rag |
| **Conversion‑Rate** | Empfehlung → Berichtsexport | reports |
| **Exploration‑Balance** | Verhältnis bekannter vs. neuer Themen | bandit logs |
| **Decision‑Latency** | Zeit von Vorschlag → Aktion (Bericht) | events |

### 3. Strategische Wirkung
| Metrik | Beschreibung | Quelle |
|--------|---------------|--------|
| **Kurskorrekturen** | pro Quartal aus Review‑Protokollen | learning loop |
| **Abweichung Prognose vs. Ist** | Energie/Budget‑Delta | timeseries |
| **Fragilitätsscore** | Volatilität / Anpassungshäufigkeit | derived |

### 4. Visualisierung (Admin‑Dashboard)
- Heatmaps (Useful/Conversion per Thema)
- Zeitverlauf (Decision Latency, Fragilität)
- Top/Flop‑Themen (Exploration Score)
- Export als CSV/PDF

### 5. Nutzung
- Dev: `make eval` erzeugt Kennzahlen
- Prod: `/api/v1/admin/metrics` liefert Aggregationen
