"""
Versendet die täglichen Job-Treffer per E-Mail über die Resend-API
(https://resend.com, kostenloses Kontingent: 100 Mails/Tag).

WICHTIG: Resends Test-Absender (onboarding@resend.dev) erlaubt ohne eigene
verifizierte Domain nur den Versand an die E-Mail-Adresse des jeweiligen
Resend-Account-Inhabers. Deshalb wird hier für jeden Empfänger ein eigener
API-Key verwendet (siehe NOTIFY_RECIPIENTS in config.py) und die Mail
entsprechend mehrfach versendet -- mit identischem Inhalt für alle.
"""
import os
from datetime import date

import requests

from src.config import NOTIFY_RECIPIENTS

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
    "moehre_digital_strategy": "Möhre: Digital Strategy & Consulting",
    "moehre_online_marketing": "Möhre: Online Marketing / Performance",
    "moehre_marketing_kommunikation": "Möhre: Marketing-Kommunikation & Kampagnen",
    "moehre_produktmarketing": "Möhre: Produktmarketing",
    "moehre_crm_marketing_automation": "Möhre: CRM & Marketing Automation",
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


def _send_single_email(api_key: str, to_email: str, subject: str, html: str) -> bool:
    """Sendet eine einzelne E-Mail über den angegebenen API-Key.
    Gibt True bei Erfolg zurück, False bei Fehler (loggt die Fehlermeldung,
    bricht aber nicht den gesamten Lauf ab, falls ein anderer Empfänger
    trotzdem erfolgreich beliefert werden kann)."""
    response = requests.post(
        RESEND_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "from": FROM_ADDRESS,
            "to": [to_email],
            "subject": subject,
            "html": html,
        },
        timeout=20,
    )

    if response.status_code >= 300:
        print(f"  [FEHLER] E-Mail-Versand an {to_email} fehlgeschlagen: "
              f"{response.status_code} {response.text}")
        return False

    print(f"  E-Mail erfolgreich versendet an {to_email}.")
    return True


def send_notification(jobs: list[dict]) -> None:
    subject = f"{len(jobs)} neue Stellenanzeige(n)" if jobs else "Job-Crawler: keine neuen Treffer heute"
    html = _build_html(jobs)

    any_success = False
    for recipient in NOTIFY_RECIPIENTS:
        api_key = os.environ.get(recipient["api_key_env"])
        if not api_key:
            print(f"  [WARNUNG] {recipient['api_key_env']} fehlt -- "
                  f"E-Mail an {recipient['email']} wird übersprungen.")
            continue
        if _send_single_email(api_key, recipient["email"], subject, html):
            any_success = True

    if not any_success:
        raise RuntimeError(
            "Keine E-Mail konnte versendet werden. Bitte prüfen, ob die "
            "RESEND_API_KEY-Secrets korrekt gesetzt sind."
        )
