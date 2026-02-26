"""
Test script for TestimonialStore.
"""
import asyncio
import os
import logging
from app.rag.testimonial_store import testimonial_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_retrieval():
    # 1. Search for a testimonial
    query = "jerawat batu di dahi"
    logger.info(f"Searching for: {query}")
    result = await testimonial_store.search_testimonial(query)
    
    if result:
        logger.info(f"Found testimonial: {result['description']}")
        logger.info(f"Image path: {result['image_path']}")
    else:
        logger.warning("No testimonial found for the query.")

    # 2. Search for a non-existent one with threshold
    query = "kucing lucu"
    logger.info(f"Searching for: {query}")
    result = await testimonial_store.search_testimonial(query, threshold=0.1)
    
    if result:
        logger.error(f"Should NOT have found anything, but found: {result['description']}")
    else:
        logger.info("Correctly found no match for unrelated query.")

if __name__ == "__main__":
    asyncio.run(test_retrieval())
