"""
Relevanz-Filter gegen lose Adzuna-Treffer.

Hintergrund: Adzunas "what"-Parameter ist KEINE exakte Phrasensuche, sondern
eine lockere Relevanzsuche über einzelne Wörter (Adzuna nutzt im eigenen
Beispiel sogar "what_exclude", um Störtreffer wie "Java" bei einer Suche nach
"JavaScript Developer" auszuschließen -- ein klares Indiz dafür). Dadurch
können fachfremde Treffer durchkommen, bei denen nur ein einzelnes,
unspezifisches Wort wie "Manager" übereinstimmt.

Dieser Filter prüft client-seitig nach dem Abruf, ob der tatsächliche
Jobtitel ausreichend mit dem Suchbegriff überlappt, der den Treffer
geliefert hat.
"""
from src.text_utils import word_overlap_ratio

# Mindestanteil der (>2-stelligen) Wörter aus dem Suchbegriff, die im
# tatsächlichen Jobtitel vorkommen müssen, damit der Treffer als relevant gilt.
RELEVANCE_THRESHOLD = 0.6


def is_relevant(job: dict) -> bool:
    search_term = job.get("search_term", "")
    title = job.get("title", "")
    if not search_term or not title:
        return True  # ohne Vergleichsbasis nicht ausschließen
    return word_overlap_ratio(search_term, title) >= RELEVANCE_THRESHOLD


def filter_relevant(jobs: list[dict]) -> list[dict]:
    kept = []
    dropped = []
    for job in jobs:
        if is_relevant(job):
            kept.append(job)
        else:
            dropped.append(job)
    print(f"  Relevanz-Filter: {len(kept)} von {len(jobs)} Treffern bestanden.")
    for job in dropped:
        print(f"    -> aussortiert (passt nicht zu '{job.get('search_term')}'): "
              f"{job['title']} @ {job['company']}")
    return kept
