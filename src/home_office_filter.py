"""
Filtert Jobs nach der Home-Office-Pflichtbedingung.
Ein Job zählt als passend, wenn Titel ODER Beschreibung eines der
Home-Office-Schlüsselwörter enthält (case-insensitive) UND dieses
Vorkommen nicht direkt verneint wird (z. B. "kein Homeoffice möglich").
"""
from src.config import HOME_OFFICE_KEYWORDS, REQUIRE_HOME_OFFICE
from src.text_utils import has_unnegated_keyword


def has_home_office(job: dict) -> bool:
    text = f"{job.get('title', '')} {job.get('description', '')}".lower()
    return has_unnegated_keyword(text, HOME_OFFICE_KEYWORDS)


def filter_home_office(jobs: list[dict]) -> list[dict]:
    """Gibt nur Jobs zurück, die die Home-Office-Bedingung erfüllen.
    Wird REQUIRE_HOME_OFFICE auf False gesetzt, kommen alle Jobs durch."""
    if not REQUIRE_HOME_OFFICE:
        return jobs

    kept = [job for job in jobs if has_home_office(job)]
    print(f"  Home-Office-Filter: {len(kept)} von {len(jobs)} Treffern bestanden.")
    return kept
