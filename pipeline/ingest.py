import os
import csv
import sqlite3
import logging
from pipeline.db import get_connection, init_db
from pipeline.skill_extractor import extract_skills
from scraper.utils.normalizer import detect_palestine_mention, clean_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RAW_FILES = [
    "data/raw/remoteok_raw.csv",
    "data/raw/weworkremotely_raw.csv",
    "data/raw/remotive_raw.csv",
    "data/raw/jobicy_raw.csv",
]

INSERT_SQL = """
    INSERT OR IGNORE INTO processed_jobs (
        source, source_tier, external_id, title, company,
        location, country_code, is_remote, skills,
        job_category, date_posted, url,
        is_palestine_mentioned, hash
    ) VALUES (
        :source, :source_tier, :external_id, :title, :company,
        :location, :country_code, :is_remote, :skills,
        :job_category, :date_posted, :url,
        :is_palestine_mentioned, :hash
    )
"""

def infer_category(title: str) -> str:
    title_lower = title.lower()
    if any(w in title_lower for w in ["data", "ml", "machine learning", "ai", "analyst"]):
        return "data_ai"
    if any(w in title_lower for w in ["devops", "cloud", "infrastructure", "sre", "platform"]):
        return "devops_cloud"
    if any(w in title_lower for w in ["frontend", "front-end", "react", "vue", "angular", "ui"]):
        return "frontend"
    if any(w in title_lower for w in ["backend", "back-end", "api", "server"]):
        return "backend"
    if any(w in title_lower for w in ["fullstack", "full stack", "full-stack"]):
        return "fullstack"
    if any(w in title_lower for w in ["mobile", "android", "ios", "flutter"]):
        return "mobile"
    if any(w in title_lower for w in ["security", "cyber", "penetration"]):
        return "security"
    return "software_engineering"

def process_row(row: dict) -> dict:
    title = clean_text(row.get("title", ""))
    company = clean_text(row.get("company", ""))

    # Combine title + skills field for extraction
    raw_skills = row.get("skills", "") or ""
    text_for_extraction = f"{title} {raw_skills}"
    extracted = extract_skills(text_for_extraction)

    location = row.get("location", "") or ""
    full_text = f"{title} {company} {location}"

    return {
        "source": row.get("source", ""),
        "source_tier": row.get("source_tier", "global"),
        "external_id": row.get("external_id", ""),
        "title": title,
        "company": company,
        "location": location,
        "country_code": row.get("country_code", ""),
        "is_remote": 1 if str(row.get("is_remote", "")).lower() in ("true", "1") else 0,
        "skills": ",".join(extracted),
        "job_category": infer_category(title),
        "date_posted": row.get("date_posted", ""),
        "url": row.get("url", ""),
        "is_palestine_mentioned": 1 if detect_palestine_mention(full_text) else 0,
        "hash": row.get("hash", ""),
    }

def run():
    init_db()
    conn = get_connection()
    total_inserted = 0
    total_skipped = 0

    for filepath in RAW_FILES:
        if not os.path.exists(filepath):
            logger.warning(f"File not found, skipping: {filepath}")
            continue

        inserted = 0
        skipped = 0

        with open(filepath, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for raw_row in reader:
                processed = process_row(raw_row)
                try:
                    conn.execute(INSERT_SQL, processed)
                    inserted += 1
                except sqlite3.IntegrityError:
                    skipped += 1

        conn.commit()
        logger.info(f"{filepath}: inserted {inserted}, skipped {skipped} duplicates")
        total_inserted += inserted
        total_skipped += skipped

    conn.close()
    logger.info(f"Ingestion complete — total inserted: {total_inserted}, skipped: {total_skipped}")

if __name__ == "__main__":
    run()