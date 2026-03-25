import feedparser
import csv
import os
import logging
from datetime import datetime
from scraper.utils.dedup import compute_hash
from scraper.utils.normalizer import is_it_job, clean_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RAW_PATH = "data/raw/weworkremotely_raw.csv"
# RSS feeds per IT category
FEEDS = [
    "https://weworkremotely.com/categories/remote-programming-jobs.rss",
    "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss",
    "https://weworkremotely.com/categories/remote-data-science-jobs.rss",
]


def run():
    logger.info("Scraping We Work Remotely RSS...")
    rows = []
    for feed_url in FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            title = clean_text(entry.get("title", ""))
            if not is_it_job(title):
                continue
            # WWR title format: "Company: Job Title"
            parts = title.split(":", 1)
            company = parts[0].strip() if len(parts) > 1 else ""
            job_title = parts[1].strip() if len(parts) > 1 else title

            rows.append(
                {
                    "source": "weworkremotely",
                    "source_tier": "remote",
                    "external_id": entry.get("id", ""),
                    "title": job_title,
                    "company": company,
                    "location": "Remote",
                    "country_code": "REMOTE",
                    "is_remote": True,
                    "skills": "",
                    "date_posted": entry.get("published", ""),
                    "url": entry.get("link", ""),
                    "hash": compute_hash("weworkremotely", job_title, company),
                    "scraped_at": datetime.now().isoformat(),
                }
            )

    os.makedirs("data/raw", exist_ok=True)
    with open(RAW_PATH, "w", newline="", encoding="utf-8") as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    logger.info(f"We Work Remotely: saved {len(rows)} IT jobs → {RAW_PATH}")
    return rows


if __name__ == "__main__":
    run()
