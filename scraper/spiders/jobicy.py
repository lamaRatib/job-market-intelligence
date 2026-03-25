import requests
import csv
import os
import logging
from datetime import datetime
from scraper.utils.dedup import compute_hash
from scraper.utils.normalizer import detect_country, clean_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RAW_PATH = "data/raw/jobicy_raw.csv"
URL = "https://jobicy.com/api/v2/remote-jobs?count=50&industry=engineering"
HEADERS = {"User-Agent": "JobMarketResearch/1.0 (academic)"}

def run():
    logger.info("Scraping Jobicy API...")
    resp = requests.get(URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    jobs = resp.json().get("jobs", [])

    rows = []
    for job in jobs:
        title = clean_text(job.get("jobTitle", ""))
        company = clean_text(job.get("companyName", ""))
        location = clean_text(job.get("jobGeo", "Worldwide"))
        skills = job.get("jobIndustry", [])
        if isinstance(skills, list):
            skills = ",".join(skills)

        rows.append({
            "source": "jobicy",
            "source_tier": "global",
            "external_id": str(job.get("id", "")),
            "title": title,
            "company": company,
            "location": location,
            "country_code": detect_country(location) or "REMOTE",
            "is_remote": True,
            "skills": skills,
            "date_posted": job.get("pubDate", ""),
            "url": job.get("url", ""),
            "hash": compute_hash("jobicy", title, company),
            "scraped_at": datetime.now().isoformat()
        })

    os.makedirs("data/raw", exist_ok=True)
    with open(RAW_PATH, "w", newline="", encoding="utf-8") as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    logger.info(f"Jobicy: saved {len(rows)} IT jobs → {RAW_PATH}")
    return rows

if __name__ == "__main__":
    run()