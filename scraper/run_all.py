import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scraper.spiders import remoteok, weworkremotely, remotive, jobicy
from pipeline.db import init_db

SCRAPERS = [
    ("RemoteOK",         remoteok),
    ("We Work Remotely", weworkremotely),
    ("Remotive",         remotive),
    ("Jobicy",           jobicy),
]

def run_all():
    init_db()
    results = {}
    for name, module in SCRAPERS:
        try:
            rows = module.run()
            results[name] = len(rows)
        except Exception as e:
            print(f"[ERROR] {name} failed: {e}")
            results[name] = 0

    print("\n── Scraping summary ──")
    total = 0
    for name, count in results.items():
        status = "✓" if count > 0 else "✗"
        print(f"  {status} {name}: {count} jobs")
        total += count
    print(f"\n  Total: {total} jobs scraped")

if __name__ == "__main__":
    run_all()