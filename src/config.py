"""
Zentrale Konfiguration des Job-Crawlers.
Hier werden Suchbegriffe, Standort und die überwachten Firmen/Institutionen gepflegt.
"""

# ---------------------------------------------------------------------------
# Standort & Radius
# ---------------------------------------------------------------------------
HOME_POSTAL_CODE = "50226"          # Frechen-Königsdorf
HOME_CITY = "Frechen"
SEARCH_RADIUS_KM = 30
ALLOW_REMOTE = True                  # Remote-Jobs unabhängig vom Radius zulassen

# Home-Office ist eine Pflichtbedingung: vollständig remote ODER hybrid mit
# Home-Office-Anteil zählt, reine Präsenzstellen werden ausgefiltert.
REQUIRE_HOME_OFFICE = True
HOME_OFFICE_KEYWORDS = [
    "homeoffice", "home-office", "home office",
    "remote", "hybrid", "mobiles arbeiten",
    "teilweise remote", "flexibles arbeiten",
]

# ---------------------------------------------------------------------------
# Suchbegriff-Sets (drei Richtungen)
# ---------------------------------------------------------------------------
SEARCH_TERMS = {
    "public_affairs": [
        "Public Affairs Manager",
        "Public Affairs Referent",
        "Politikberater",
        "Referent Politik",
        "Government Relations Manager",
        "Verbandsreferent",
        "Referent Interessenvertretung",
        "Stakeholder Manager",
    ],
    "nachhaltigkeit_energie": [
        "Referent Nachhaltigkeit",
        "ESG Manager",
        "ESG Referent",
        "Referent Energiepolitik",
        "Klimapolitik Referent",
        "Nachhaltigkeitsmanager Regulatorik",
    ],
    "strategie_projektmanagement": [
        "Referent Strategie",
        "Projektmanager Politik",
        "Strategiereferent",
        "Projektkoordinator Verwaltung",
    ],
}

# ---------------------------------------------------------------------------
# Firmen/Institutionen für die direkte Karriereseiten-Überwachung
# Jede Firma hat: Name, Karriere-URL (best bekannte Einstiegsseite),
# und ob sie sich außerhalb des 30-km-Radius befindet (dann zählt nur
# explizit remote/home-office-fähige Stellen).
# ---------------------------------------------------------------------------
COMPANIES = [
    # --- Energie / Industrie ---
    {"name": "REWE Group", "career_url": "https://www.rewe-group-karriere.com/jobsuche/", "out_of_radius": False},
    {"name": "RheinEnergie", "career_url": "https://www.rheinenergie.com/de/karriere/", "out_of_radius": False},
    {"name": "RWE", "career_url": "https://www.rwe.com/karriere/jobsuche/", "out_of_radius": False},
    {"name": "Uniper", "career_url": "https://www.uniper.energy/karriere/jobsuche", "out_of_radius": False},
    {"name": "Henkel", "career_url": "https://www.henkel.de/karriere/jobsuche", "out_of_radius": False},
    {"name": "Vodafone Deutschland", "career_url": "https://careers.vodafone.com/de/", "out_of_radius": False},
    {"name": "Rheinmetall", "career_url": "https://rheinmetall.jobs/", "out_of_radius": False},
    {"name": "Metro AG", "career_url": "https://www.metroag.de/karriere/jobsuche", "out_of_radius": False},
    {"name": "CECONOMY", "career_url": "https://www.ceconomy.de/karriere/", "out_of_radius": False},
    {"name": "Lanxess", "career_url": "https://lanxess.com/de/Karriere/Jobsuche", "out_of_radius": False},
    {"name": "Covestro", "career_url": "https://www.covestro.com/de/karriere/jobsuche", "out_of_radius": False},
    {"name": "Currenta", "career_url": "https://www.currenta.de/karriere/jobboerse", "out_of_radius": False},
    {"name": "Deutsche Post DHL Group", "career_url": "https://careers.dhl.com/global/de/search-results", "out_of_radius": False},

    # --- NRW Landesgesellschaften / öffentlicher Sektor ---
    {"name": "NRW.Energy4Climate", "career_url": "https://karriere.energy4climate.nrw/stellen", "out_of_radius": False},
    {"name": "LANUK NRW", "career_url": "https://www.lanuk.nrw.de/das-lanuk/karriere-im-lanuk/aktuelle-stellenangebote", "out_of_radius": False},
    {"name": "Stadt Köln", "career_url": "https://www.stadt-koeln.de/service/stellenangebote/", "out_of_radius": False},

    # NRW-Landesministerien laufen zentral über karriere.nrw
    {"name": "Staatskanzlei NRW", "career_url": "https://karriere.nrw/", "out_of_radius": False},
    {"name": "Ministerium für Wirtschaft, Industrie, Klimaschutz und Energie NRW", "career_url": "https://karriere.nrw/", "out_of_radius": False},
    {"name": "Ministerium der Finanzen NRW", "career_url": "https://karriere.nrw/", "out_of_radius": False},
    {"name": "Ministerium des Innern NRW", "career_url": "https://karriere.nrw/", "out_of_radius": False},
    {"name": "Ministerium für Kinder, Jugend, Familie, Gleichstellung, Flucht und Integration NRW", "career_url": "https://karriere.nrw/", "out_of_radius": False},
    {"name": "Ministerium für Arbeit, Gesundheit und Soziales NRW", "career_url": "https://karriere.nrw/", "out_of_radius": False},
    {"name": "Ministerium für Schule und Bildung NRW", "career_url": "https://karriere.nrw/", "out_of_radius": False},
    {"name": "Ministerium für Heimat, Kommunales, Bau und Digitalisierung NRW", "career_url": "https://karriere.nrw/", "out_of_radius": False},
    {"name": "Ministerium der Justiz NRW", "career_url": "https://karriere.nrw/", "out_of_radius": False},
    {"name": "Ministerium für Umwelt, Naturschutz und Verkehr NRW", "career_url": "https://karriere.nrw/", "out_of_radius": False},
    {"name": "Ministerium für Landwirtschaft und Verbraucherschutz NRW", "career_url": "https://karriere.nrw/", "out_of_radius": False},
    {"name": "Ministerium für Kultur und Wissenschaft NRW", "career_url": "https://karriere.nrw/", "out_of_radius": False},
    {"name": "Minister für Bundes- und Europaangelegenheiten NRW", "career_url": "https://karriere.nrw/", "out_of_radius": False},

    # --- Außerhalb des Radius, nur remote/home-office-Treffer zählen ---
    {"name": "Projektträger Jülich", "career_url": "https://www.ptj.de/karriere/stellenangebote", "out_of_radius": True},

    # --- Beratung ---
    {"name": "Rebel Deutschland", "career_url": "https://www.rebelgroup.com/de/karriere", "out_of_radius": False},
]

# ---------------------------------------------------------------------------
# Verifizierungs-Einstellungen
# ---------------------------------------------------------------------------
# Pfade, die zusätzlich zur career_url für das automatische Domain-Raten
# bei unbekannten Firmen probiert werden.
GUESS_CAREER_PATHS = ["/karriere", "/jobs", "/careers", "/karriere/jobs", "/de/karriere"]

# ---------------------------------------------------------------------------
# E-Mail
# ---------------------------------------------------------------------------
NOTIFY_EMAIL = "lukas.verhofstad@gmail.com"

# ---------------------------------------------------------------------------
# Datenablage (Duplikat-Erkennung)
# ---------------------------------------------------------------------------
SEEN_JOBS_FILE = "data/seen_jobs.json"
