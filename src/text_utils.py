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
