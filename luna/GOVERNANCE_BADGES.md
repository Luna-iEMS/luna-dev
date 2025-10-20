# GOVERNANCE BADGES — Dokumentstatus

| Feld | Beschreibung | Typ |
|------|---------------|-----|
| **owner** | Verantwortliche Person/Abteilung | string |
| **valid_until** | Gültigkeitsdatum | date |
| **approved_by** | Freigeber (Name/Initialen) | string |
| **status** | ["gültig","prüfen","veraltet"] | enum |

## Darstellung (UI)
Badges im Customer‑Dashboard & Admin‑Korpus‑Ansicht:
- 🟢 gültig
- 🟡 prüfen
- 🔴 veraltet

Diese Metadaten werden im `items.metadata`‑JSON gespeichert und bei Ingestion vergeben.
