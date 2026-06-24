"""
Sucht Stellenanzeigen über die Adzuna-API (kostenlose Stufe ausreichend).
Adzuna deckt u.a. Indeed-, StepStone- und weitere Portal-Inhalte ab.

Benötigte Umgebungsvariablen (als GitHub Secrets gepflegt):
  ADZUNA_APP_ID
  ADZUNA_APP_KEY
"""
import os
import time
import requests

ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs/de/search/1"


def search_adzuna(keyword: str, postal_code: str, radius_km: int, results_per_page: int = 30) -> list[dict]:
    """Führt eine einzelne Suche gegen die Adzuna-API aus und gibt eine Liste
    normalisierter Job-Dicts zurück."""
    app_id = os.environ.get("ADZUNA_APP_ID")
    app_key = os.environ.get("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        raise RuntimeError(
            "ADZUNA_APP_ID/ADZUNA_APP_KEY fehlen. Bitte als Umgebungsvariablen "
            "bzw. GitHub Secrets setzen (kostenloser Account auf adzuna.com/about/api)."
        )

    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": keyword,
        "where": postal_code,
        "distance": radius_km,
        "results_per_page": results_per_page,
        "content-type": "application/json",
    }

    try:
        response = requests.get(ADZUNA_BASE_URL, params=params, timeout=20)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"  [WARNUNG] Adzuna-Suche für '{keyword}' fehlgeschlagen: {exc}")
        return []

    payload = response.json()
    jobs = []
    for item in payload.get("results", []):
        jobs.append({
            "id": f"adzuna:{item.get('id')}",
            "title": item.get("title", "").strip(),
            "company": (item.get("company") or {}).get("display_name", "Unbekannt"),
            "location": (item.get("location") or {}).get("display_name", ""),
            "latitude": item.get("latitude"),
            "longitude": item.get("longitude"),
            "url": item.get("redirect_url", ""),
            "description": item.get("description", ""),
            "created": item.get("created", ""),
            "search_term": keyword,
            "source": "adzuna",
        })
    return jobs


def search_all_terms(search_terms_by_category: dict, postal_code: str, radius_km: int) -> list[dict]:
    """Durchsucht alle konfigurierten Suchbegriffe und gibt die zusammengeführte,
    nach Job-ID deduplizierte Liste zurück."""
    all_jobs: dict[str, dict] = {}

    for category, terms in search_terms_by_category.items():
        for term in terms:
            print(f"  Suche: '{term}' ({category}) ...")
            results = search_adzuna(term, postal_code, radius_km)
            for job in results:
                job["category"] = category
                # Falls derselbe Job über mehrere Suchbegriffe gefunden wird,
                # behalten wir den ersten Treffer (Kategorie bleibt erhalten).
                all_jobs.setdefault(job["id"], job)
            # Kleine Pause, um das kostenlose Rate-Limit nicht zu strapazieren.
            time.sleep(1)

    return list(all_jobs.values())
