"""
Verwaltet die Liste bereits gesehener Job-IDs in einer JSON-Datei,
damit der Crawler nicht jeden Tag dieselben Treffer meldet.
"""
import json
import os
from datetime import datetime, timezone

from src.config import SEEN_JOBS_FILE


def load_seen_ids() -> set[str]:
    if not os.path.exists(SEEN_JOBS_FILE):
        return set()
    with open(SEEN_JOBS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return set(data.get("seen_ids", []))


def save_seen_ids(seen_ids: set[str]) -> None:
    os.makedirs(os.path.dirname(SEEN_JOBS_FILE), exist_ok=True)
    payload = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "seen_ids": sorted(seen_ids),
    }
    with open(SEEN_JOBS_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def filter_new_jobs(jobs: list[dict]) -> list[dict]:
    """Gibt nur Jobs zurück, deren ID noch nicht gesehen wurde, und
    aktualisiert anschließend die Seen-Liste (inkl. Speichern)."""
    seen_ids = load_seen_ids()
    new_jobs = [job for job in jobs if job["id"] not in seen_ids]

    updated_ids = seen_ids | {job["id"] for job in jobs}
    save_seen_ids(updated_ids)

    print(f"  Duplikat-Check: {len(new_jobs)} neue von {len(jobs)} Treffern "
          f"({len(seen_ids)} bereits bekannt).")
    return new_jobs
