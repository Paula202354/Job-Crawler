# Job-Crawler

Automatisierter, täglich laufender Crawler für Stellenanzeigen im Umkreis von
30&nbsp;km um Frechen-Königsdorf (inkl. Remote-Stellen), mit Aktualitätsprüfung
gegen die Original-Karriereseiten der Unternehmen.

## Funktionsweise

1. **Suche** über die Adzuna-API mit drei Suchbegriff-Sets (Public Affairs,
   Nachhaltigkeit/Energie, Strategie/Projektmanagement).
2. **Home-Office-Filter**: nur Stellen mit Remote-/Hybrid-/Home-Office-Hinweis.
3. **Vollzeit/Unbefristet-Filter**: schließt Werkstudenten-, Praktikums-,
   Trainee- und sonstige kategorisch befristete/Teilzeit-Stellen aus, sowie
   Stellen mit explizitem Befristungs- oder Teilzeit-Hinweis.
4. **Duplikat-Check**: Stellen, die bereits gemeldet wurden, werden nicht erneut verschickt.
5. **Verifizierung**: Für jeden neuen Treffer wird versucht, die Stelle auf
   der Original-Karriereseite des Unternehmens zu finden (Aktualitätsprüfung).
   Ergebnis wird als „verifiziert“ oder „ungeprüft“ markiert — beides wird
   verschickt, nur halt unterschiedlich gekennzeichnet.
6. **E-Mail**: Versand der neuen Treffer per Resend an deine Adresse.

Läuft automatisch **einmal täglich** über GitHub Actions — kein eigener Server nötig.

## Einmaliges Setup

### 1. Accounts anlegen (beide kostenlos)

- **Adzuna**: Registrierung auf https://developer.adzuna.com/ → `App ID` und `App Key` notieren.
- **Resend**: Registrierung auf https://resend.com/ → API-Key erstellen unter *API Keys*.
  Für den Einstieg reicht der Test-Absender `onboarding@resend.dev`, später kann
  eine eigene Domain verifiziert werden.

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
| `RESEND_API_KEY` | dein Resend API-Key |

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
