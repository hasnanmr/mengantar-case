"""
Seed script to populate the testimonial store with initial data.
"""
import asyncio
import os
import logging
from app.rag.testimonial_store import testimonial_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_testimonials():
    await testimonial_store.initialize_store()
    
    testimonials = [
        {
            "image_path": "testimonials/testi_01.jpg",
            "description": "Jerawat merah meradang di pipi membaik setelah 1 minggu.",
        },
        {
            "image_path": "testimonials/testi_02.jpg",
            "description": "Jerawat batu di dahi mengempes dalam 3 hari penggunaan rutin.",
        },
        {
            "image_path": "testimonials/testi_03.jpg",
            "description": "Bekas jerawat memudar signifikan setelah 2 minggu pakai Acne Care.",
        },
    ]
    
    # Ensure directory exists
    os.makedirs("static/testimonials", exist_ok=True)
    
    # In a real scenario, you'd have actual images. 
    # For this demo, we'll create placeholder files if they don't exist.
    for t in testimonials:
        full_path = os.path.join("static", t["image_path"])
        if not os.path.exists(full_path):
            with open(full_path, "wb") as f:
                f.write(b"placeholder")
            logger.info(f"Created placeholder image at {full_path}")
            
        await testimonial_store.add_testimonial(t["image_path"], t["description"])
        logger.info(f"Seeded testimonial: {t['description']}")

if __name__ == "__main__":
    asyncio.run(seed_testimonials())
