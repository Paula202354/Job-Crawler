# Job-Crawler

Automatisierter, täglich laufender Crawler für Stellenanzeigen im Umkreis von
30&nbsp;km um Frechen-Königsdorf (inkl. Remote-Stellen), mit Aktualitätsprüfung
gegen die Original-Karriereseiten der Unternehmen.

**Dieses Repository wird von zwei Personen gemeinsam genutzt** (Lukas und
Möhre) -- beide erhalten dieselbe tägliche Mail mit allen Treffern aus allen
Kategorien. Die Kategorie-Überschriften in der Mail zeigen, aus wessen
Suchrichtung ein Treffer stammt.

## Funktionsweise

1. **Suche** über die Adzuna-API mit drei Suchbegriff-Sets (Public Affairs,
   Nachhaltigkeit/Energie, Strategie/Projektmanagement).
2. **Relevanz-Filter**: prüft, ob der tatsächliche Jobtitel wirklich zum
   Suchbegriff passt, der ihn gefunden hat (Adzunas eigene Suche ist
   keine exakte Phrasensuche, siehe "Behobene Bugs" unten).
3. **Entfernungs-Filter**: eigene Entfernungsberechnung per Haversine-Formel
   anhand der von Adzuna mitgelieferten Koordinaten, statt sich allein auf
   den "distance"-Parameter der API zu verlassen. Jobs mit Home-Office-Hinweis
   sind vom Radius ausgenommen.
4. **Home-Office-Filter**: nur Stellen mit Remote-/Hybrid-/Home-Office-Hinweis.
5. **Vollzeit/Unbefristet-Filter**: schließt Werkstudenten-, Praktikums-,
   Trainee- und sonstige kategorisch befristete/Teilzeit-Stellen aus, sowie
   Stellen mit explizitem Befristungs- oder Teilzeit-Hinweis.
6. **Duplikat-Check**: Stellen, die bereits gemeldet wurden, werden nicht erneut verschickt.
7. **Verifizierung**: Für jeden neuen Treffer wird versucht, die Stelle auf
   der Original-Karriereseite des Unternehmens zu finden (Aktualitätsprüfung).
   Ergebnis wird als „verifiziert“ oder „ungeprüft“ markiert — beides wird
   verschickt, nur halt unterschiedlich gekennzeichnet.
8. **E-Mail**: Versand der neuen Treffer per Resend an deine Adresse.

Läuft automatisch **einmal täglich** über GitHub Actions — kein eigener Server nötig.

## Einmaliges Setup

### 1. Accounts anlegen (beide kostenlos)

- **Adzuna**: Registrierung auf https://developer.adzuna.com/ → `App ID` und `App Key` notieren.
- **Resend (für Lukas)**: Registrierung auf https://resend.com/ mit
  `lukas.verhofstad@gmail.com` → API-Key erstellen unter *API Keys*.
- **Resend (für Möhre)**: **Zweiter, eigener** Account auf https://resend.com/
  mit `miri.eckardt@gmail.com` registrieren → eigenen API-Key erstellen.

  **Wichtig, warum zwei Accounts nötig sind**: Resends kostenloser
  Test-Absender (`onboarding@resend.dev`) erlaubt ohne eigene verifizierte
  Domain nur den Versand an die E-Mail-Adresse, mit der der jeweilige
  Resend-Account registriert wurde. Ein einzelner Account könnte also nicht
  an beide Adressen gleichzeitig senden -- deshalb braucht jede Person ihren
  eigenen Account und eigenen API-Key, auch wenn beide dieselbe Mail erhalten.

### 2. Repository auf GitHub anlegen

```bash
cd job-crawler
git init
git add .
git commit -m "Initial commit: Job-Crawler"
git branch -M main
git remote add origin <DEINE_REPO_URL>
git push -u origin main
```

### 3. Secrets in GitHub hinterlegen

Im Repository: **Settings → Secrets and variables → Actions → New repository secret**

| Name | Wert |
|---|---|
| `ADZUNA_APP_ID` | deine Adzuna App-ID |
| `ADZUNA_APP_KEY` | dein Adzuna App-Key |
| `RESEND_API_KEY` | Lukas' Resend API-Key |
| `RESEND_API_KEY_MOEHRE` | Möhres Resend API-Key |

### 4. Workflow testen

Im Reiter **Actions** den Workflow „Job Crawler“ auswählen und über
**Run workflow** (workflow_dispatch) manuell einmal anstoßen, um zu prüfen,
ob alles funktioniert, bevor der tägliche Zeitplan greift.

## Lokales Testen (optional)

```bash
pip install -r requirements.txt
export ADZUNA_APP_ID=...
export ADZUNA_APP_KEY=...
export RESEND_API_KEY=...
python -m src.main
```

## Anpassungen

- **Suchbegriffe / Firmenliste / Standort**: alles in `src/config.py`.
- **Zeitplan**: `.github/workflows/crawler.yml`, Zeile mit `cron:`.
- **E-Mail-Layout**: `src/notifier.py`.

## Behobene Bugs (Versionshinweis)

Beim ersten echten Lauf tauchten zwei klar fachfremde Treffer auf (ein Google-Job
in Barcelona, ein Treffer aus dem medizinischen Controlling). Ursache: Adzunas
`what`-Parameter ist keine exakte Phrasensuche, sondern eine lockere
Relevanzsuche über Einzelwörter -- bei "Public Affairs Manager" reichte
offenbar schon das Wort "Manager" allein. Behoben durch:
- einen Relevanz-Filter (`src/relevance_filter.py`), der den gefundenen
  Jobtitel gegen den ursprünglichen Suchbegriff prüft,
- einen Entfernungs-Filter (`src/distance_filter.py`) mit eigener
  Haversine-Berechnung anhand der von Adzuna mitgelieferten Koordinaten,
  statt sich allein auf den API-Parameter zu verlassen.

Außerdem behoben: Die Liste bekannter Job-IDs (`data/seen_jobs.json`) wurde
ursprünglich per `git commit` + `git push` ins Repository zurückgeschrieben.
Das führte wiederholt zu "rejected, fetch first"-Fehlern, sobald gleichzeitig
manuell gepusht oder der Workflow mehrfach kurz hintereinander getestet
wurde (klassische Race Condition bei parallelen Git-Pushes auf dieselbe
Datei). Behoben durch einen Architekturwechsel: Die Liste wird jetzt über
GitHub's **Cache-Mechanismus** (`actions/cache`) zwischen den Läufen
gespeichert, nicht mehr per Git-Commit. Dadurch kann dieser Konflikt
grundsätzlich nicht mehr auftreten, da kein Push mehr nötig ist. Zusätzlich
verhindert eine `concurrency`-Einstellung, dass zwei Läufe überhaupt
gleichzeitig starten.

## Bekannte Einschränkungen

- Manche Karriereseiten laden Inhalte erst per JavaScript nach (z. B. über
  Bewerbermanagementsysteme wie Personio oder SAP). Der einfache HTML-Abruf
  sieht solche Inhalte nicht — betroffene Treffer werden dann als „ungeprüft“
  statt „verifiziert“ markiert, aber trotzdem verschickt.
- Die automatische Domain-Erkennung für Firmen außerhalb der festen Liste ist
  eine einfache Heuristik (`firmenname.de`) und wird nicht immer treffen.
- Der Vollzeit/Unbefristet-Filter erkennt Anstellungsart und Befristung anhand
  von Schlüsselwörtern in Titel/Beschreibung. Enthält die (ggf. von Adzuna
  gekürzte) Beschreibung gar keinen Hinweis auf Vollzeit/Teilzeit oder
  Befristung, wird die Stelle bewusst NICHT ausgeschlossen, um keine
  tatsächlich passenden Treffer zu verlieren. Bei den ersten Läufen lohnt
  sich ein Blick, ob das in der Praxis zu viele oder zu wenige Treffer
  durchlässt — die Schlüsselwortlisten lassen sich in
  `src/employment_filter.py` leicht anpassen.
- Der Entfernungs-Filter lässt Jobs außerhalb des 30-km-Radius durch, sobald
  irgendein Home-Office-Hinweis vorliegt -- auch bei "hybrid" oder "teilweise
  Homeoffice", was bei großer Distanz (z. B. ein anderes Land) praktisch nicht
  umsetzbar wäre. Aktuell wird das bewusst nicht zusätzlich eingeschränkt; bei
  Bedarf lässt sich das in `src/distance_filter.py` verschärfen (z. B. nur noch
  "vollständig remote" statt jedes Home-Office-Hinweises als Ausnahme).
- Der GitHub-Cache, in dem die Liste bekannter Job-IDs liegt, wird laut
  GitHub automatisch entfernt, wenn er 7 Tage lang nicht genutzt wurde.
  Da der Crawler täglich läuft und den Cache dabei jedes Mal neu beschreibt,
  ist das in der Praxis kein Problem -- nur falls der Workflow mal länger
  als eine Woche pausiert (z. B. Urlaub, Repository-Wartung), würde die
  Duplikat-Erkennung danach einmalig wieder von Null starten.
