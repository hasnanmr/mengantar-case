"""
RAG system: build and query FAISS index from product knowledge.
"""
import os
import logging
import pickle
from typing import List

import faiss
import numpy as np
import pickle
from typing import List

from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _get_embeddings_model():
    """Get the OpenAIEmbeddings model configured for OpenRouter."""
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openrouter_api_key,
        openai_api_base=settings.openrouter_base_url,
    )


def _get_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using the OpenRouter API."""
    embeddings_model = _get_embeddings_model()
    return embeddings_model.embed_documents(texts)


def build_faiss_index():
    """Build FAISS index from product knowledge chunks."""
    from knowledge.product_knowledge import PRODUCT_KNOWLEDGE

    # Define headers to split on
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
    ]

    # Split by headers
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    md_header_splits = markdown_splitter.split_text(PRODUCT_KNOWLEDGE)

    # Further split with RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=250,
        chunk_overlap=25,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    splits = text_splitter.split_documents(md_header_splits)

    # Process chunks to include header context
    chunks = []
    for split in splits:
        metadata = split.metadata
        header_context = " > ".join([metadata.get(f"Header {i}", "") for i in range(1, 3) if metadata.get(f"Header {i}")])
        content = f"[{header_context}] {split.page_content}" if header_context else split.page_content
        chunks.append(content.strip())

    logger.info(f"Building FAISS index from {len(chunks)} knowledge chunks...")

    embeddings = _get_embeddings(chunks)
    embeddings_np = np.array(embeddings, dtype=np.float32)
    dimension = embeddings_np.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_np)

    os.makedirs(settings.faiss_index_path, exist_ok=True)
    faiss.write_index(index, os.path.join(settings.faiss_index_path, "index.faiss"))
    with open(os.path.join(settings.faiss_index_path, "chunks.pkl"), "wb") as f:
        pickle.dump(chunks, f)

    logger.info(f"FAISS index saved to {settings.faiss_index_path}")
    return index, chunks


def query_knowledge(query: str, top_k: int = 3) -> str:
    """Retrieve the most relevant knowledge chunks for a given query."""
    index_path = os.path.join(settings.faiss_index_path, "index.faiss")
    chunks_path = os.path.join(settings.faiss_index_path, "chunks.pkl")

    if not os.path.exists(index_path):
        logger.warning("FAISS index not found. Returning empty context.")
        return ""

    index = faiss.read_index(index_path)
    with open(chunks_path, "rb") as f:
        chunks = pickle.load(f)

    query_embedding = _get_embeddings([query])
    query_embedding_np = np.array(query_embedding, dtype=np.float32)
    distances, indices = index.search(query_embedding_np, top_k)

    results = [chunks[i] for i in indices[0] if i < len(chunks)]
    return "\n\n".join(results)


if __name__ == "__main__":
    build_faiss_index()
