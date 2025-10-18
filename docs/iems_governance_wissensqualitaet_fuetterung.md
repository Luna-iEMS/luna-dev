# Wissensqualität & Fütterung – internes Steuerdokument für Luna’s Brain

---

## 1. Zweck & Geltungsbereich

Dieses Dokument definiert die Richtlinien, Prozesse und Standards für den Umgang mit Wissen innerhalb von **Luna’s Brain**. Es richtet sich an alle internen Teams, die Inhalte erstellen, prüfen oder freigeben. Ziel ist es, sicherzustellen, dass alle Informationen, die in das System einfließen, **verlässlich**, **kontextualisiert** und **antifragil** sind – also das System mit jeder neuen Erfahrung besser machen.

---

## 2. Grundprinzipien

Luna’s Brain basiert auf der Annahme, dass Wissen kein statisches Archiv ist, sondern ein lebendiges System. Damit dieses System aus Veränderungen, Fehlern und Widersprüchen lernen kann, gelten folgende Grundprinzipien:

1. **Klarheit vor Komplexität** – Informationen sollen verständlich, nachvollziehbar und eindeutig sein.
2. **Kontext statt Absolutheit** – jede Aussage gilt nur innerhalb ihres beschriebenen Rahmens.
3. **Widerspruch als Lernsignal** – Abweichungen sind kein Fehler, sondern Rohstoff für Lernen.
4. **Verknüpfbarkeit statt Vollständigkeit** – Wissen ist wertvoll, wenn es sich verbinden lässt, nicht wenn es isoliert perfekt ist.
5. **Transparenz in Herkunft und Verantwortung** – jedes Wissen ist rückverfolgbar zu Quelle, Autor und Zeitpunkt.

---

## 3. Definition: Was gilt als „Wissen“?

Im Rahmen von Luna’s Brain gilt ein Dokument oder Datensatz als *Wissen*, wenn er mindestens drei Eigenschaften erfüllt:

1. **Erklärungswert** – der Inhalt beschreibt Zusammenhänge, nicht nur Fakten.  
2. **Anwendbarkeit** – die Information kann Entscheidungen, Modelle oder Strategien unterstützen.  
3. **Kontextbezug** – der Ursprung, Zeitraum und Wirkungsraum sind klar benannt.

Beispiele für akzeptierte Wissensformen:
- Module und Playbook-Dokumente
- Interne Analysen und Erfahrungsberichte
- Fallbeispiele aus Projekten
- Erkenntnisse aus Pilotphasen oder Fehleranalysen
- Regulatorische Dokumente (in aufbereiteter Form)

Nicht als Wissen gelten:
- Rohdaten ohne Beschreibung
- Einzelstatements ohne Kontext
- Meinungen ohne Kennzeichnung oder Quelle

---

## 4. Qualitätsdimensionen

Jedes Wissen wird entlang von sieben Dimensionen bewertet:

| Dimension | Leitfrage | Ziel | Bewertungsstufe |
|------------|------------|------|----------------|
| **Faktizität** | Ist es überprüfbar und belegt? | Belege oder Quellen vorhanden | 0–1 |
| **Kontextualität** | Ist der Geltungsrahmen beschrieben? | Ort, Zeit, Situation klar | 0–1 |
| **Kausalität** | Werden Ursachen und Wirkungen erklärt? | Verknüpfte Logik vorhanden | 0–1 |
| **Relevanz** | Unterstützt es eine Entscheidung oder ein Modell? | Bezug zu Zielen | 0–1 |
| **Kohärenz** | Passt es zu bestehendem Wissen? | Keine unaufgelösten Widersprüche | 0–1 |
| **Klarheit** | Ist es sprachlich verständlich? | Präzise, aktiv, konkret | 0–1 |
| **Verknüpfbarkeit** | Ist es mit anderen Themen verbunden? | Tags, Module, Referenzen | 0–1 |

Gesamtbewertung: Durchschnitt aller sieben Dimensionen → **Qualitätsscore (0–1)**  
> 0.85–1.00 = exzellent · 0.65–0.84 = gut · 0.45–0.64 = überarbeiten · <0.45 = nicht einspielen

---

## 5. Arten von Wissen in Luna’s Brain

| Kategorie | Beschreibung | Beispiel |
|------------|--------------|-----------|
| **Strukturiertes Wissen** | Formale Prozesse, Definitionen, Modelle | Energieflussmodell, CO₂-Berechnung, IEMS-Framework |
| **Situatives Wissen** | Erfahrungsberichte, Lessons Learned, Beobachtungen | Pilotprojekt LunaGrid 2025, Reaktionen auf Preisvolatilität |
| **Diskursives Wissen** | Offene Fragen, Widersprüche, Hypothesen | Strategische Optionen für Speicherflexibilität |

Antifragilität entsteht durch das Zusammenspiel aller drei Kategorien. Jede neue Information kann bestehendes Wissen ergänzen, in Frage stellen oder neu gewichten.

---

## 6. Der Fütterungsprozess

### 6.1. Phase 1 – Rohaufnahme
- Dokumente werden in das System geladen (z. B. `.docx`, `.pdf`, `.md`).
- Automatische Analyse erkennt:
  - Thema, Zielgruppe, Hauptaussagen
  - Unsicherheiten und mögliche Quellen
  - Vorschläge für Metadaten und Tags
- Ergebnis: ein *vorläufiger Wissenseintrag*, der noch nicht freigegeben ist.

### 6.2. Phase 2 – Menschliche Validierung
- Der Wissenskurator prüft:
  - Stimmt Thema und Kontext?  
  - Ist die Information aktuell und belegbar?  
  - Fehlen Bezüge zu anderen Modulen oder Themen?
- Ergänzungen:
  - Tags, Quellen, Version, Status („aktiv“, „historisch“, „in Prüfung“)
  - Anmerkungen zu Unsicherheiten oder offenen Punkten

### 6.3. Phase 3 – Integration
- Nach Freigabe wird der Eintrag in die Wissensbasis übernommen.
- Das System verknüpft ihn mit bestehenden Inhalten, bewertet Qualität und Version.
- Alte Versionen bleiben archiviert, aber markiert (`superseded_by`, `archived`).

### 6.4. Phase 4 – Laufendes Lernen
- Nutzerinteraktionen (Suchanfragen, Lesezeit, Feedback) fließen in die Relevanzbewertung ein.
- Das System erkennt Muster: Welche Dokumente werden häufig genutzt, welche erzeugen Konflikte?
- Konflikte und Widersprüche werden als Lernsignale markiert und automatisch zur Überprüfung vorgeschlagen.

---

## 7. Metadaten-Standard

Jedes Dokument enthält Metadaten, die Kontext, Verantwortung und Status definieren.

| Feld | Beschreibung | Beispiel |
|-------|--------------|----------|
| **title** | Kurzer, beschreibender Titel | „Lastprognosemodell Q3/2025“ |
| **author** | Verantwortliche Person oder Team | „Monika Pichlhöfer / Data Strategy“ |
| **created / updated** | Zeitstempel | 2025‑10‑15 |
| **version** | Laufende Dokumentversion | 1.2 |
| **source** | Herkunft (intern, regulatorisch, extern) | „intern“ |
| **audience** | Zielgruppe | „interne Analyse / Strategie“ |
| **topics** | Thematische Tags | [energie, prognose, antifragilität] |
| **dependencies** | Verweise auf verwandte Module | [module_03_prognose, module_05_finanz] |
| **status** | Aktivitätsstatus | aktiv / archiviert / in_review |
| **confidence** | Einschätzung der inhaltlichen Sicherheit | 0.8 |
| **quality_score** | Systembewertung | 0.92 |

---

## 8. Rollen & Verantwortlichkeiten

| Rolle | Aufgabe | Häufigkeit |
|--------|----------|-------------|
| **Autor:in / Fachexpert:in** | Erstellt oder lädt Wissen hoch | bei Bedarf |
| **Wissenskurator:in** | Prüft Struktur, Metadaten, Kontext | je Upload |
| **Fachreviewer:in** | Bewertet Richtigkeit und Relevanz | 1× je Quartal |
| **Projektleitung (Luna Core)** | Legt Prioritäten und Reviewzyklen fest | halbjährlich |
| **System (KI)** | Automatische Analyse, Bewertung, Versionierung | kontinuierlich |

---

## 9. Umgang mit Unsicherheiten & Widersprüchen

**Unsicherheiten** werden nicht gelöscht, sondern dokumentiert.  
Formulierungsvorschläge:
- „Die Datengrundlage ist unvollständig, Schätzung auf Basis…“
- „Diese Aussage gilt unter der Annahme, dass…“

**Widersprüche** werden als Lernsignale behandelt:
- Das System markiert betroffene Dokumente (`conflicts_with`).
- Eine Review-Aufgabe wird ausgelöst.
- Beide Versionen bleiben sichtbar, bis ein neuer Konsens entsteht.

**Veraltetes Wissen** wird historisiert:
- Alte Dokumente bleiben abrufbar.
- Neue Versionen verlinken rückwärts (`supersedes`).

> Antifragilität heißt: Wir löschen nicht, wir lernen aus Unterschieden.

---

## 10. Qualitätsmetriken & Reporting

Jedes Quartal wird ein Bericht zur Wissensqualität erstellt. Er enthält:

- Durchschnittlicher Qualitätsscore aller aktiven Einträge
- Anzahl neuer, geprüfter und archivierter Dokumente
- Konflikt- und Unsicherheitsraten (z. B. wie viele Dokumente widersprüchlich sind)
- Nutzungstrends (z. B. meistgelesene Module)

Diese Kennzahlen dienen nicht zur Kontrolle einzelner Personen, sondern zur Steuerung der Wissensentwicklung.

---

## 11. Pflege & Aktualisierung

- Jede Wissenseinheit wird mindestens **halbjährlich überprüft**.  
- Bei regulatorischen Themen erfolgt eine **Ad-hoc-Prüfung**, sobald sich externe Rahmenbedingungen ändern.  
- Archivierte Inhalte bleiben zugänglich, aber getrennt von aktivem Wissen.  
- Feedback aus der Nutzung (Fehlinterpretationen, Ergänzungsbedarf) wird gesammelt und fließt in die Überarbeitung ein.

---

## 12. Interne Checklisten

### **Vor dem Upload**
- [ ] Ist der Kontext klar (Ziel, Zeitraum, Quelle)?
- [ ] Sind Fakten belegt oder nachvollziehbar?
- [ ] Gibt es einen Bezug zu bestehenden Modulen?
- [ ] Enthält der Text klare Aussagen und Unsicherheiten?
- [ ] Ist die Sprache eindeutig und präzise?

### **Nach der Freigabe**
- [ ] Wurde der Qualitätsscore berechnet?
- [ ] Sind Metadaten vollständig?
- [ ] Gibt es offene Konflikte oder Ergänzungen?
- [ ] Wurde die Version dokumentiert?

---

## 13. Wissensethik

Luna’s Brain verpflichtet sich zu:
- **Transparenz** in Quellen und Begründungen,  
- **Nachvollziehbarkeit** in Entscheidungen,  
- **Fehlerfreundlichkeit** als Prinzip des Fortschritts,  
- **Lernfähigkeit** durch Konfrontation mit Unsicherheiten,  
- und **Respekt vor Kontext** – Wissen gilt nie absolut.

---

## 14. Schlussprinzip

> „Nicht Perfektion ist das Ziel, sondern Anpassungsfähigkeit. Wissen, das sich verändern darf, bleibt wahr.“

Diese Richtlinie ist lebendig. Sie wird weiterentwickelt, sobald neue Formen des Lernens, Arbeitens oder Denkens im System entstehen.

---

**Stand:** 15. Oktober 2025  
**Erstellt von:** Luna Core Team / Data Strategy  
**Gültigkeit:** intern – nicht zur externen Weitergabe.

