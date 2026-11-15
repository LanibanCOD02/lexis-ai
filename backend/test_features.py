import asyncio
import json
import logging
from app.db.session import AsyncSessionLocal
from sqlalchemy.future import select
from app.models.core import Case
from app.api.endpoints.cases import summarize_case, extract_principles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_case_features():
    async with AsyncSessionLocal() as db:
        # Fetch a case
        stmt = select(Case).limit(1)
        result = await db.execute(stmt)
        case = result.scalars().first()
        
        if not case:
            logger.error("No case found in the database. Cannot run test.")
            return

        logger.info(f"Testing features for Case ID: {case.id} ({case.title})")
        
        # Test Case Summarization
        logger.info("\n--- Test 1: Generate Case Summary ---")
        try:
            summary = await summarize_case(case.id, db)
            logger.info("Summary generated successfully!")
            logger.info(json.dumps(summary, indent=2))
            
            # Verify DB Persistence
            await db.refresh(case)
            if case.summary:
                logger.info("Summary was correctly persisted to the cases table.")
            else:
                logger.error("Summary was NOT persisted to the cases table.")
        except Exception as e:
            logger.error(f"Failed to generate case summary: {e}")

        # Test Principle Extraction
        logger.info("\n--- Test 2: Extract Legal Principles ---")
        try:
            principles = await extract_principles(case.id, db)
            logger.info(f"Extracted {len(principles)} principles successfully!")
            for p in principles:
                logger.info(f"- Title: {p['principle_title']}")
                logger.info(f"  Confidence: {p['confidence_score']}")
                logger.info(f"  Page: {p['page_number']}")
                logger.info(f"  Supporting Chunk: {p['supporting_chunk_id']}")
                logger.info(f"  Text snippet: {p['principle_text'][:100]}...")
        except Exception as e:
            logger.error(f"Failed to extract principles: {e}")

if __name__ == "__main__":
    asyncio.run(test_case_features())
