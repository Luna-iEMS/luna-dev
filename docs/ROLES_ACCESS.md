# ROLES & ACCESS — Rollenmodell Luna‑IEMS

## Übersicht
| Rolle | Dashboard | Sichtbarkeit | Aktionen |
|--------|------------|---------------|-----------|
| **Admin** | Admin‑UI | Alle Daten | Benutzer, Uploads, Monitoring, Rechte |
| **CFO** | Customer‑UI | Finanzen, Budgets, Effizienz | Reports, Bewertung, Feedback |
| **Technik** | Customer‑UI | Verbrauch, Anlagen, Märkte | Simulation, Szenarien, Feedback |
| **ESG** | Customer‑UI | CO₂, Nachhaltigkeit, Maßnahmen | Bewertung, Berichtsexport |
| **Controlling** | Customer‑UI | Kennzahlen, Benchmarks | Reports, Korrekturvorschläge |

## Authentifizierung
- JWT (`role`‑Claim)
- API‑Scopes (z. B. `data:read`, `recommend:read`, `admin:write`)
- später: OIDC‑Integration

## Rollen‑UI‑Mapping
- CFO: Fokus Wirtschaftlichkeit
- Technik: Fokus Effizienz
- ESG: Fokus Nachhaltigkeit
- Controlling: Fokus Kennzahlen, Wirkung
