"""
Versendet die täglichen Job-Treffer per E-Mail über die Resend-API
(https://resend.com, kostenloses Kontingent: 100 Mails/Tag).

Benötigte Umgebungsvariable: RESEND_API_KEY
"""
import os
from datetime import date

import requests

from src.config import NOTIFY_EMAIL

RESEND_URL = "https://api.resend.com/emails"
# Resend verlangt eine verifizierte Absender-Domain ODER den Test-Absender
# 'onboarding@resend.dev' für den kostenlosen Einstieg.
FROM_ADDRESS = os.environ.get("RESEND_FROM_ADDRESS", "Job-Crawler <onboarding@resend.dev>")

STATUS_LABELS = {
    "verified": "✅ verifiziert (auf Original-Karriereseite gefunden)",
    "unverified": "⚠️ ungeprüft (nicht eindeutig auf Original-Seite bestätigt)",
    "unknown": "❔ Verifizierung nicht möglich",
}

CATEGORY_LABELS = {
    "public_affairs": "Public Affairs / Politikberatung",
    "nachhaltigkeit_energie": "Nachhaltigkeit / Energie-Regulierung",
    "strategie_projektmanagement": "Strategie / Projektmanagement",
}


def _build_html(jobs: list[dict]) -> str:
    if not jobs:
        return "<p>Heute keine neuen passenden Stellenanzeigen gefunden.</p>"

    # Nach Kategorie gruppieren für eine übersichtliche Mail
    by_category: dict[str, list[dict]] = {}
    for job in jobs:
        by_category.setdefault(job.get("category", "sonstige"), []).append(job)

    sections = []
    for category, category_jobs in by_category.items():
        label = CATEGORY_LABELS.get(category, category)
        items = []
        for job in category_jobs:
            status_label = STATUS_LABELS.get(job.get("verification_status"), "")
            radius_note = " · außerhalb 30-km-Radius, nur wegen Remote-Option gelistet" if job.get("out_of_radius") else ""
            distance_note = f" · ca. {job['distance_km']} km entfernt" if job.get("distance_km") is not None else ""
            items.append(f"""
                <li style="margin-bottom: 14px;">
                    <a href="{job['url']}" style="font-weight: bold; font-size: 15px;">{job['title']}</a><br>
                    <span>{job['company']} – {job.get('location', '')}{distance_note}</span><br>
                    <span style="font-size: 13px; color: #555;">{status_label}{radius_note}</span>
                </li>
            """)
        sections.append(f"<h3>{label}</h3><ul>{''.join(items)}</ul>")

    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px;">
        <h2>Neue Stellenanzeigen vom {date.today().strftime('%d.%m.%Y')}</h2>
        {''.join(sections)}
        <p style="font-size: 12px; color: #888; margin-top: 24px;">
            Automatisch erstellt von deinem Job-Crawler.
        </p>
    </div>
    """


def send_notification(jobs: list[dict]) -> None:
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        raise RuntimeError("RESEND_API_KEY fehlt. Bitte als Umgebungsvariable/GitHub Secret setzen.")

    subject = f"{len(jobs)} neue Stellenanzeige(n)" if jobs else "Job-Crawler: keine neuen Treffer heute"

    response = requests.post(
        RESEND_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "from": FROM_ADDRESS,
            "to": [NOTIFY_EMAIL],
            "subject": subject,
            "html": _build_html(jobs),
        },
        timeout=20,
    )

    if response.status_code >= 300:
        print(f"  [FEHLER] E-Mail-Versand fehlgeschlagen: {response.status_code} {response.text}")
        response.raise_for_status()
    else:
        print(f"  E-Mail erfolgreich versendet an {NOTIFY_EMAIL}.")
