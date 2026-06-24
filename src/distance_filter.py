"""
Eigene Entfernungsprüfung statt blindem Vertrauen in Adzunas "where"/"distance"-
Parameter. Hintergrund: Trotz dieser Parameter tauchte z.B. ein Treffer aus
Barcelona auf -- weit außerhalb des 30-km-Radius. Adzuna liefert pro Treffer
Latitude/Longitude mit, die wir hier selbst gegen den Heimatstandort prüfen
(Haversine-Formel = Luftlinienentfernung auf einer Kugel).

Jobs mit einem Home-Office-Hinweis sind von dieser Prüfung ausgenommen
(siehe ALLOW_REMOTE in config.py) -- das war ja explizit gewünscht
("Remote-Jobs sind auch möglich").
"""
import math

from src.config import ALLOW_REMOTE, HOME_LATITUDE, HOME_LONGITUDE, SEARCH_RADIUS_KM
from src.home_office_filter import has_home_office

EARTH_RADIUS_KM = 6371.0


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(math.radians, [lat1, lon1, lat2, lon2])
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return EARTH_RADIUS_KM * c


def is_within_radius_or_remote(job: dict) -> bool:
    lat = job.get("latitude")
    lon = job.get("longitude")

    # Keine Koordinaten von Adzuna übermittelt -> kann nicht geprüft werden,
    # nicht vorsorglich ausschließen (z.B. bei rein remote ausgeschriebenen Stellen
    # ohne festen Standort).
    if lat is None or lon is None:
        return True

    distance_km = haversine_distance_km(HOME_LATITUDE, HOME_LONGITUDE, lat, lon)
    job["distance_km"] = round(distance_km, 1)

    if distance_km <= SEARCH_RADIUS_KM:
        return True

    if ALLOW_REMOTE and has_home_office(job):
        return True

    return False


def filter_by_distance(jobs: list[dict]) -> list[dict]:
    kept = []
    dropped = []
    for job in jobs:
        if is_within_radius_or_remote(job):
            kept.append(job)
        else:
            dropped.append(job)
    print(f"  Entfernungs-Filter: {len(kept)} von {len(jobs)} Treffern bestanden.")
    for job in dropped:
        print(f"    -> aussortiert (zu weit entfernt, {job.get('distance_km')} km, "
              f"kein Remote-Hinweis): {job['title']} @ {job['company']} "
              f"({job.get('location')})")
    return kept
