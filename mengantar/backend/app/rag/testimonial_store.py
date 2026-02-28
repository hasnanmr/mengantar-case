"""
Testimonial Store: Save and retrieve image-based testimonials using FAISS and PostgreSQL.
"""
import os
import logging
import pickle
import faiss
import numpy as np
from typing import Optional
import psycopg
import psycopg.rows

from app.core.config import get_settings
from app.rag.knowledge_base import _get_embeddings

logger = logging.getLogger(__name__)
settings = get_settings()


class TestimonialStore:
    def __init__(self):
        self.db_url = settings.database_url
        self.faiss_dir = os.path.join(settings.faiss_index_path, "testimonials")
        self.index_path = os.path.join(self.faiss_dir, "index.faiss")
        self.metadata_path = os.path.join(self.faiss_dir, "metadata.pkl")

        os.makedirs(self.faiss_dir, exist_ok=True)

    async def initialize_store(self):
        """
        Verify the testimonials table exists.
        Table is created via Alembic migration (020_user_create_testimonials_table).
        This method is kept for compatibility but performs a lightweight check.
        """
        async with await psycopg.AsyncConnection.connect(self.db_url) as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'mengantar_test'
                        AND table_name = 'testimonials'
                    )
                """)
                row = await cur.fetchone()
                if not row or not row[0]:
                    raise RuntimeError(
                        "Testimonials table not found. "
                        "Please run: uv run alembic upgrade head"
                    )
        logger.info("Testimonial store verified.")

    async def add_testimonial(self, image_path: str, description: str):
        """Add a testimonial to PostgreSQL and update FAISS index."""
        # 1. Save to PostgreSQL
        async with await psycopg.AsyncConnection.connect(self.db_url) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT INTO mengantar_test.testimonials (image_path, description) "
                    "VALUES (%s, %s) RETURNING id",
                    (image_path, description),
                )
                row = await cur.fetchone()
                testimonial_id = row[0]
            await conn.commit()

        # 2. Update FAISS
        embedding = _get_embeddings([description])[0]
        # OpenRouter returns a raw list, not a numpy array.
        dimension = len(embedding)

        if os.path.exists(self.index_path):
            index = faiss.read_index(self.index_path)
            with open(self.metadata_path, "rb") as f:
                metadata = pickle.load(f)
        else:
            index = faiss.IndexFlatL2(dimension)
            metadata = []

        index.add(np.array([embedding], dtype=np.float32))
        metadata.append({"id": testimonial_id, "description": description})

        faiss.write_index(index, self.index_path)
        with open(self.metadata_path, "wb") as f:
            pickle.dump(metadata, f)

        logger.info(f"Added testimonial ID {testimonial_id} to store.")

    async def search_testimonial(self, query: str, top_k: int = 1, threshold: float = 1.0) -> Optional[dict]:
        """Search for the most relevant testimonial."""
        if not os.path.exists(self.index_path):
            logger.warning("FAISS index for testimonials not found.")
            return None

        index = faiss.read_index(self.index_path)
        with open(self.metadata_path, "rb") as f:
            metadata = pickle.load(f)

        query_embedding = _get_embeddings([query])
        query_embedding_np = np.array(query_embedding, dtype=np.float32)
        distances, indices = index.search(query_embedding_np, top_k)

        best_idx = indices[0][0]
        best_distance = distances[0][0]

        if best_idx == -1 or best_idx >= len(metadata):
            return None

        if best_distance > threshold:
            logger.info(f"Best match distance {best_distance} exceeds threshold {threshold}.")
            return None

        testimonial_metadata = metadata[best_idx]
        testimonial_id = testimonial_metadata["id"]

        async with await psycopg.AsyncConnection.connect(self.db_url) as conn:
            async with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                await cur.execute(
                    "SELECT * FROM mengantar_test.testimonials WHERE id = %s",
                    (testimonial_id,),
                )
                row = await cur.fetchone()
                if row:
                    image_path = row["image_path"]
                    if ".." in image_path or image_path.startswith("/"):
                        logger.error(f"Potential path traversal detected in DB: {image_path}")
                        return None
                    return dict(row)

        return None


testimonial_store = TestimonialStore()
