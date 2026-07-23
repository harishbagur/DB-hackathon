"""
Similarity search using pgvector + sentence-transformers.

The model (all-MiniLM-L6-v2) is loaded once at startup.
It produces 384-dimensional embeddings that match the vector(384)
column in knowledge_article.

Usage:
    from app.core.similarity import search, embed_text
"""
from __future__ import annotations

from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text

# Loaded once — ~80 MB, downloads on first run if not cached
try:
    from sentence_transformers import SentenceTransformer
    _model = SentenceTransformer("all-MiniLM-L6-v2")
    _EMBEDDINGS_AVAILABLE = True
except Exception:
    _model = None
    _EMBEDDINGS_AVAILABLE = False


def embed_text(text_input: str) -> List[float]:
    """Return a 384-dim embedding for a string."""
    if not _EMBEDDINGS_AVAILABLE or _model is None:
        # Fallback: zero vector — search will still run, results will be random
        return [0.0] * 384
    return _model.encode(text_input).tolist()


def search(query: str, db: Session, k: int = 10) -> List[dict]:
    """
    Find the top-k knowledge articles most similar to `query`.
    Returns a list of dicts with article_number, title, category, score.
    """
    embedding = embed_text(query)

    rows = db.execute(
        text("""
            SELECT
                article_number,
                title,
                category,
                status,
                1 - (embedding <=> CAST(:embedding AS vector)) AS score
            FROM knowledge_article
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :k
        """),
        {"embedding": str(embedding), "k": k},
    ).fetchall()

    return [
        {
            "article_number": row.article_number,
            "title": row.title,
            "category": row.category,
            "score": round(float(row.score), 2),
        }
        for row in rows
    ]


def update_embedding(article_id: int, content: str, db: Session) -> None:
    """
    Generate and store an embedding for a knowledge article.
    Call this whenever an article is created or its content changes.
    """
    embedding = embed_text(content)
    db.execute(
        text("""
            UPDATE knowledge_article
            SET embedding = CAST(:embedding AS vector)
            WHERE article_id = :article_id
        """),
        {"embedding": str(embedding), "article_id": article_id},
    )
    db.commit()
