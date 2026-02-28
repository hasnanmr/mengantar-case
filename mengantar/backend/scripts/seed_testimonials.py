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
            "image_path": "testimonials/amanda.jpg",
            "description": "Oke banget sih buat perawatan jerawat! Awalnya aku cuma pake obat totol jerawatnya cocok banget akhirnya nyoba si facial washnya. Cocok, calming dan ngebantu redain jerawat yang lagi meradang.",
        },
        {
            "image_path": "testimonials/silmi.jpg",
            "description": "Udah pake ini dari tahun 2023, selalu repurchase karena cocok banget sama kulitku yang acne-prone, bikin kulit jarang jerawat dan sehat, teksturnya kayak ada scrub kecil tapi ga sakit sama sekali, busa nya ada tapi gak to much.",
        },
    ]
    
    for t in testimonials:
        await testimonial_store.add_testimonial(t["image_path"], t["description"])
        logger.info(f"Seeded testimonial: {t['description']}")

if __name__ == "__main__":
    asyncio.run(seed_testimonials())
