"""
Gemeinsame Hilfsfunktionen für die Schlüsselwort-Erkennung in Stellenanzeigen,
inkl. einfacher Verneinungserkennung. Wird von mehreren Filtern verwendet
(Home-Office-Filter, Anstellungsart-Filter, ...).
"""
import re

# Wörter, die ein nahestehendes Schlüsselwort verneinen.
NEGATION_WORDS = ["kein", "keine", "keinen", "nicht", "ohne", "ausgeschlossen", "leider"]
# Wie viele Wörter vor dem Treffer auf eine Verneinung geprüft werden.
NEGATION_WINDOW_BEFORE = 3
# Nach dem Treffer wird ein größeres Fenster geprüft, weil deutsche Verneinungen
# durch die Verbklammer oft erst später im Satz stehen
# (z. B. "Homeoffice ist bei uns leider nicht möglich").
NEGATION_WINDOW_AFTER = 6


def is_negated(text: str, match_start: int, match_end: int) -> bool:
    """Prüft auf eine Verneinung sowohl VOR der Fundstelle
    (z. B. "kein Homeoffice") als auch DANACH
    (z. B. "Homeoffice ist bei uns nicht möglich")."""
    preceding_words = re.findall(r"\w+", text[:match_start])[-NEGATION_WINDOW_BEFORE:]
    following_words = re.findall(r"\w+", text[match_end:])[:NEGATION_WINDOW_AFTER]
    return any(word in NEGATION_WORDS for word in preceding_words + following_words)


def has_unnegated_keyword(text: str, keywords: list[str]) -> bool:
    """Gibt True zurück, wenn mindestens eines der keywords im (bereits
    kleingeschriebenen) Text vorkommt UND an dieser Stelle nicht verneint wird."""
    for keyword in keywords:
        for match in re.finditer(re.escape(keyword), text):
            if not is_negated(text, match.start(), match.end()):
                return True
    return False


def normalize(text: str) -> str:
    """Vereinfacht einen Text für den groben Wortabgleich:
    Kleinschreibung, (m/w/d)-Zusätze und Mehrfach-Whitespace entfernen."""
    text = text.lower()
    text = re.sub(r"\(?[mwdx/]{3,}\)?", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def word_overlap_ratio(reference_text: str, candidate_text: str) -> float:
    """Gibt den Anteil der (>2-stelligen) Wörter aus reference_text zurück,
    die als Substring in candidate_text vorkommen (beide vorher normalisiert).
    Substring-Suche statt exaktem Wortabgleich, damit deutsche Komposita wie
    "Strategiereferent" bei der Suche nach "Referent" trotzdem treffen."""
    normalized_reference = normalize(reference_text)
    normalized_candidate = normalize(candidate_text)
    words = [w for w in normalized_reference.split() if len(w) > 2]
    if not words:
        return 0.0
    hits = sum(1 for w in words if w in normalized_candidate)
    return hits / len(words)
