"""
Prüft, ob ein über ein Jobportal gefundener Treffer auch auf der
Original-Karriereseite des Unternehmens aktuell gelistet ist.

Drei mögliche Ergebnisse pro Job:
  "verified"   -> Originalseite bekannt UND Jobtitel dort gefunden
  "unverified" -> Originalseite bekannt, aber Titel nicht eindeutig gefunden,
                  ODER Firma unbekannt und automatisches Raten erfolglos
  "unknown"    -> kein Verifizierungsversuch möglich (z.B. Netzwerkfehler)

Wichtig: "unverified" schließt einen Job NICHT aus (siehe Vorgabe von Lukas),
sondern wird nur als Markierung in der E-Mail mitgegeben.
"""
import re
import requests
from urllib.parse import urlparse

from src.config import COMPANIES, GUESS_CAREER_PATHS

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; JobCrawler/1.0; persönlicher Gebrauch)"}

# Firmenname -> career_url Lookup, einmalig aufgebaut
_COMPANY_LOOKUP = {c["name"].lower(): c for c in COMPANIES}


def _normalize(text: str) -> str:
    """Vereinfacht einen Text für den groben Titel-Abgleich:
    Kleinschreibung, (m/w/d)-Zusätze und Mehrfach-Whitespace entfernen."""
    text = text.lower()
    text = re.sub(r"\(?[mwdx/]{3,}\)?", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _fetch(url: str) -> str | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            return resp.text
    except requests.RequestException:
        pass
    return None


def _title_appears_in_page(job_title: str, page_html: str) -> bool:
    normalized_title = _normalize(job_title)
    normalized_page = _normalize(page_html)
    # Bei kurzen Titeln (<3 Wörter) verlangen wir den ganzen Titel als Substring,
    # bei längeren reicht es, wenn die meisten Kernwörter vorkommen.
    words = [w for w in normalized_title.split() if len(w) > 2]
    if not words:
        return False
    hits = sum(1 for w in words if w in normalized_page)
    return hits / len(words) >= 0.7


def _guess_career_page(company_name: str) -> str | None:
    """Best-effort: versucht, anhand des Firmennamens eine Karriereseite zu
    erraten, wenn die Firma nicht in unserer COMPANIES-Liste steht."""
    # Sehr einfache Heuristik: domain = firmenname ohne Leerzeichen/Sonderzeichen + .de
    slug = re.sub(r"[^a-z0-9]", "", company_name.lower())
    if not slug:
        return None
    base_domain = f"https://www.{slug}.de"
    for path in GUESS_CAREER_PATHS:
        candidate = base_domain + path
        html = _fetch(candidate)
        if html:
            return candidate
    return None


def verify_job(job: dict) -> str:
    """Gibt 'verified', 'unverified' oder 'unknown' zurück."""
    company_name = job.get("company", "")
    company_entry = _COMPANY_LOOKUP.get(company_name.lower())

    career_url = company_entry["career_url"] if company_entry else _guess_career_page(company_name)
    if not career_url:
        return "unverified"

    html = _fetch(career_url)
    if html is None:
        return "unknown"

    if _title_appears_in_page(job["title"], html):
        return "verified"
    return "unverified"


def verify_jobs(jobs: list[dict]) -> list[dict]:
    """Reichert jeden Job um den Schlüssel 'verification_status' an."""
    for job in jobs:
        status = verify_job(job)
        job["verification_status"] = status
        out_of_radius = False
        company_entry = _COMPANY_LOOKUP.get(job.get("company", "").lower())
        if company_entry:
            out_of_radius = company_entry.get("out_of_radius", False)
        job["out_of_radius"] = out_of_radius
        print(f"    -> {job['title']} @ {job['company']}: {status}"
              f"{' (außerhalb Radius)' if out_of_radius else ''}")
    return jobs
