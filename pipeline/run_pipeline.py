import sys, os, logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from scraper.run_all import run_all as run_scrapers
from pipeline.ingest import run as run_ingest
from pipeline.aggregator import run as run_aggregator
from models.classifier import train, apply_to_db
from analytics.gap_analysis import get_remote_readiness, compute_skill_gap

def main():
    logger.info("═══ Step 1: Scraping ═══")
    run_scrapers()

    logger.info("\n═══ Step 2: Ingestion + skill extraction ═══")
    run_ingest()

    logger.info("\n═══ Step 3: Skill aggregation ═══")
    run_aggregator()

    logger.info("\n═══ Step 4: ML — train classifier ═══")
    model = train()
    if model:
        apply_to_db()
        logger.info("Job categories written to DB")

    logger.info("\n═══ Step 4: ML — remote readiness scores ═══")
    top_remote = get_remote_readiness(10)
    logger.info(f"Top remote-ready jobs:\n{top_remote.to_string(index=False)}")

    logger.info("\n═══ Step 4: ML — example skill gap ═══")
    gap = compute_skill_gap(["python", "sql"])
    logger.info(f"Coverage score: {gap['coverage_score']}%")
    logger.info("Top recommendations:")
    for r in gap["recommendations"]:
        logger.info(f"  [{r['priority']}] {r['skill']} — {r['global_demand_count']} jobs")

    logger.info("\n═══ Pipeline complete ═══")

if __name__ == "__main__":
    main()