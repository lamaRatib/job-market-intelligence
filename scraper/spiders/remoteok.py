import requests
import json
import csv
import os
import logging
from datetime import datetime
from scraper.utils.dedup import compute_hash
from scraper.utils.normalizer import detect_remote, detect_country, is_it_job, clean_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RAW_PATH = "data/raw/remoteok_raw.csv"
URL = "https://remoteok.com/api"
HEADERS = {"User-Agent": "JobMarketResearch/1.0 (academic)"}

def run():
    logger.info("Scraping RemoteOK...")
    resp = requests.get(URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    jobs = [j for j in resp.json() if isinstance(j, dict) and "id" in j]

    os.makedirs("data/raw", exist_ok=True)
    rows = []
    for job in jobs:
        title = clean_text(job.get("position", ""))
        if not is_it_job(title):
            continue
        rows.append({
            "source": "remoteok",
            "source_tier": "remote",
            "external_id": str(job.get("id", "")),
            "title": title,
            "company": clean_text(job.get("company", "")),
            "location": "Remote",
            "country_code": detect_country(job.get("location", "")) or "REMOTE",
            "is_remote": True,
            "skills": ",".join(job.get("tags", [])),
            "date_posted": job.get("date", ""),
            "url": job.get("url", ""),
            "hash": compute_hash("remoteok", title, job.get("company", "")),
            "scraped_at": datetime.now().isoformat()
        })

    with open(RAW_PATH, "w", newline="", encoding="utf-8") as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    logger.info(f"RemoteOK: saved {len(rows)} IT jobs → {RAW_PATH}")
    return rows

if __name__ == "__main__":
    run()