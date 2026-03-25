import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("═══ Step 1: Scraping ═══")
    from scraper.run_all import run_all
    run_all()

    logger.info("\n═══ Step 2: Ingestion + skill extraction ═══")
    from pipeline.ingest import run as run_ingest
    run_ingest()

    logger.info("\n═══ Step 3: Skill aggregation ═══")
    from pipeline.aggregator import run as run_aggregator
    run_aggregator()

    logger.info("\n═══ Pipeline complete ═══")
    logger.info("Database ready at data/processed/jobs.db")

if __name__ == "__main__":
    main()