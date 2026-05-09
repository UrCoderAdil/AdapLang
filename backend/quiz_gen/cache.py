"""
pgvector-based question deduplication and retrieval.
Uses sentence-transformers to embed question text.
"""
from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

_EMBED_MODEL = None


def _get_embed_model():
    global _EMBED_MODEL
    if _EMBED_MODEL is None:
        from sentence_transformers import SentenceTransformer  # type: ignore
        _EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _EMBED_MODEL


def embed(text: str) -> list[float]:
    """Embed a string using a local sentence-transformer model."""
    model = _get_embed_model()
    return model.encode(text, normalize_embeddings=True).tolist()


def is_duplicate(question_text: str, db_conn, threshold: float = 0.92) -> bool:
    """
    Return True if a semantically similar question already exists in Postgres.
    Requires pgvector extension and questions.embedding column.
    """
    try:
        from pgvector.psycopg2 import register_vector  # type: ignore
        register_vector(db_conn)

        embedding = embed(question_text)
        with db_conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1 FROM questions
                WHERE 1 - (embedding <=> %s::vector) > %s
                LIMIT 1
                """,
                (embedding, threshold),
            )
            return cur.fetchone() is not None
    except Exception as exc:
        logger.warning("Duplicate check failed (skipping): %s", exc)
        return False


def store_embedding(question_id: str, question_text: str, db_conn) -> None:
    """Compute and persist the embedding for a question."""
    try:
        from pgvector.psycopg2 import register_vector  # type: ignore
        register_vector(db_conn)

        embedding = embed(question_text)
        with db_conn.cursor() as cur:
            cur.execute(
                "UPDATE questions SET embedding = %s::vector WHERE id = %s",
                (embedding, question_id),
            )
        db_conn.commit()
    except Exception as exc:
        logger.warning("Failed to store embedding: %s", exc)
