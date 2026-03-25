import requests
import csv
import os
import logging
from datetime import datetime
from scraper.utils.dedup import compute_hash
from scraper.utils.normalizer import detect_country, clean_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RAW_PATH = "data/raw/remotive_raw.csv"
URL = "https://remotive.com/api/remote-jobs?category=software-dev&limit=100"
HEADERS = {"User-Agent": "JobMarketResearch/1.0 (academic)"}

def run():
    logger.info("Scraping Remotive API...")
    resp = requests.get(URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    jobs = resp.json().get("jobs", [])

    rows = []
    for job in jobs:
        title = clean_text(job.get("title", ""))
        company = clean_text(job.get("company_name", ""))
        location = clean_text(job.get("candidate_required_location", "Worldwide"))
        tags = [t.strip() for t in job.get("tags", [])]

        rows.append({
            "source": "remotive",
            "source_tier": "global",
            "external_id": str(job.get("id", "")),
            "title": title,
            "company": company,
            "location": location,
            "country_code": detect_country(location) or "REMOTE",
            "is_remote": True,
            "skills": ",".join(tags),
            "date_posted": job.get("publication_date", ""),
            "url": job.get("url", ""),
            "hash": compute_hash("remotive", title, company),
            "scraped_at": datetime.now().isoformat()
        })

    os.makedirs("data/raw", exist_ok=True)
    with open(RAW_PATH, "w", newline="", encoding="utf-8") as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    logger.info(f"Remotive: saved {len(rows)} IT jobs → {RAW_PATH}")
    return rows

if __name__ == "__main__":
    run()