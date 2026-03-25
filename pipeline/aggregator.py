import sqlite3
import logging
from collections import Counter
from pipeline.db import get_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPSERT_SQL = """
    INSERT INTO skill_counts (skill, source_tier, count)
    VALUES (?, ?, ?)
    ON CONFLICT(skill, source_tier) DO UPDATE SET count = count + excluded.count
"""

def run():
    conn = get_connection()

    # Fetch all skills grouped by source_tier
    rows = conn.execute(
        "SELECT skills, source_tier FROM processed_jobs WHERE skills != ''"
    ).fetchall()

    tier_counters: dict[str, Counter] = {}

    for row in rows:
        skills_str = row["skills"]
        tier = row["source_tier"]
        if not skills_str:
            continue
        skills = [s.strip() for s in skills_str.split(",") if s.strip()]
        if tier not in tier_counters:
            tier_counters[tier] = Counter()
        tier_counters[tier].update(skills)

    # Clear existing counts and rewrite (idempotent)
    conn.execute("DELETE FROM skill_counts")

    for tier, counter in tier_counters.items():
        for skill, count in counter.items():
            conn.execute(UPSERT_SQL, (skill, tier, count))

    conn.commit()

    # Log top 10 global skills
    top = conn.execute("""
        SELECT skill, SUM(count) as total
        FROM skill_counts
        GROUP BY skill
        ORDER BY total DESC
        LIMIT 10
    """).fetchall()

    logger.info("Top 10 skills across all sources:")
    for row in top:
        logger.info(f"  {row['skill']:<25} {row['total']}")

    conn.close()
    logger.info("Aggregation complete → skill_counts table updated")

if __name__ == "__main__":
    run()