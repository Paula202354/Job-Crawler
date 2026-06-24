"""
Filtert Jobs nach Anstellungsart: nur Vollzeit UND unbefristet.

Logik (analog zum Home-Office-Filter, also mit Verneinungserkennung):
  - Kategorische Ausschlüsse (per Definition befristet/Teilzeit):
    Werkstudent, Praktikum, Trainee, Minijob, Ausbildung, Elternzeitvertretung etc.
  - "Teilzeit" wird nur dann zum Ausschlussgrund, wenn KEIN Vollzeit-Hinweis
    in derselben Anzeige steht (z. B. "Voll- oder Teilzeit" bleibt erlaubt).
  - "Befristet"-Hinweise (auch z. B. "befristet auf 2 Jahre", "Zeitvertrag")
    führen zum Ausschluss.
  - Wird in der Anzeige gar keine Angabe zur Anstellungsart/Befristung
    gemacht (z. B. wegen abgeschnittener Beschreibung), wird die Stelle NICHT
    ausgeschlossen, da sonst zu viele tatsächlich passende Stellen verloren
    gingen. Das ist eine bewusste Abwägung, siehe README.
"""
from src.text_utils import has_unnegated_keyword

REQUIRE_FULL_TIME_PERMANENT = True

# Diese Begriffe schließen eine Stelle unabhängig vom Rest kategorisch aus,
# weil sie per Definition keine unbefristete Vollzeit-Festanstellung sind.
HARD_EXCLUDE_KEYWORDS = [
    "werkstudent", "werkstudentin", "praktikum", "praktikant", "praktikantin",
    "trainee", "minijob", "aushilfe", "nebenjob", "ausbildung", "volontariat",
    "elternzeitvertretung", "krankheitsvertretung",
]

FULL_TIME_KEYWORDS = [
    "vollzeit", "full-time", "full time", "40-stunden-woche",
    # Häufige deutsche Kurzschreibweise, bei der "Vollzeit" nicht als
    # eigenes Wort auftaucht, sondern mit "Teilzeit" kombiniert wird:
    "voll- oder teilzeit", "voll-/teilzeit", "voll- und teilzeit",
    "vollzeit oder teilzeit", "teilzeit oder vollzeit",
]
PART_TIME_KEYWORDS = ["teilzeit", "part-time", "part time"]

PERMANENT_KEYWORDS = ["unbefristet", "permanent"]
FIXED_TERM_KEYWORDS = [
    "befristet", "befristung", "zeitvertrag", "vertretung",
    "auf 2 jahre befristet", "auf zwei jahre befristet", "auf ein jahr befristet",
]


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def is_full_time(text: str) -> bool:
    has_full = has_unnegated_keyword(text, FULL_TIME_KEYWORDS)
    has_part = has_unnegated_keyword(text, PART_TIME_KEYWORDS)
    # Ausschluss nur, wenn explizit NUR Teilzeit erwähnt wird.
    if has_part and not has_full:
        return False
    return True


def is_permanent(text: str) -> bool:
    # "unbefristet" enthält als Zeichenkette zufällig "befristet" -- das würde
    # sonst fälschlich als Befristungs-Hinweis gewertet werden (genaues
    # Gegenteil der eigentlichen Aussage). Daher vor der Prüfung entfernen.
    text_without_unbefristet = text.replace("unbefristet", "")
    return not has_unnegated_keyword(text_without_unbefristet, FIXED_TERM_KEYWORDS)


def matches_employment_type(job: dict) -> bool:
    text = f"{job.get('title', '')} {job.get('description', '')}".lower()

    if _contains_any(text, HARD_EXCLUDE_KEYWORDS):
        return False

    return is_full_time(text) and is_permanent(text)


def filter_employment_type(jobs: list[dict]) -> list[dict]:
    """Gibt nur Jobs zurück, die Vollzeit UND unbefristet sind
    (bzw. bei denen kein klares Gegensignal gefunden wurde)."""
    if not REQUIRE_FULL_TIME_PERMANENT:
        return jobs

    kept = [job for job in jobs if matches_employment_type(job)]
    print(f"  Vollzeit/Unbefristet-Filter: {len(kept)} von {len(jobs)} Treffern bestanden.")
    return kept
