"""
Hauptskript des Job-Crawlers.
Ablauf: Suche -> Home-Office-Filter -> Vollzeit/Unbefristet-Filter ->
        Duplikat-Check -> Verifizierung -> E-Mail.

Aufruf: python -m src.main
"""
from src.config import HOME_POSTAL_CODE, SEARCH_RADIUS_KM, SEARCH_TERMS
from src.adzuna_search import search_all_terms
from src.home_office_filter import filter_home_office
from src.employment_filter import filter_employment_type
from src.dedup import filter_new_jobs
from src.verification import verify_jobs
from src.notifier import send_notification


def run() -> None:
    print("=== Job-Crawler gestartet ===")

    print("\n[1/6] Suche auf Jobportalen ...")
    all_jobs = search_all_terms(SEARCH_TERMS, HOME_POSTAL_CODE, SEARCH_RADIUS_KM)
    print(f"  Insgesamt {len(all_jobs)} Treffer (vor Filterung).")

    print("\n[2/6] Home-Office-Filter ...")
    home_office_jobs = filter_home_office(all_jobs)

    print("\n[3/6] Vollzeit/Unbefristet-Filter ...")
    employment_filtered_jobs = filter_employment_type(home_office_jobs)

    print("\n[4/6] Duplikat-Check gegen bisherige Treffer ...")
    new_jobs = filter_new_jobs(employment_filtered_jobs)

    if not new_jobs:
        print("\n[5/6] Keine neuen Treffer -> keine Verifizierung nötig.")
        print("\n[6/6] Sende Status-Mail (0 neue Treffer) ...")
        send_notification([])
        print("\n=== Fertig ===")
        return

    print(f"\n[5/6] Verifizierung von {len(new_jobs)} neuen Treffern gegen Original-Karriereseiten ...")
    verified_jobs = verify_jobs(new_jobs)

    print("\n[6/6] Sende E-Mail-Benachrichtigung ...")
    send_notification(verified_jobs)

    print("\n=== Fertig ===")


if __name__ == "__main__":
    run()
