"""
Similarity search — SQLite-compatible fallback using keyword matching.

When PostgreSQL + pgvector is available, uses vector cosine similarity.
When SQLite is used (hackathon mode), falls back to simple keyword LIKE search.

Usage:
    from app.core.similarity import search, embed_text
"""
from __future__ import annotations

from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.knowledge import KnowledgeArticle


def embed_text(text_input: str) -> List[float]:
    """Return a 384-dim embedding for a string (stub for SQLite mode)."""
    return [0.0] * 384


def search(query: str, db: Session, k: int = 10) -> List[dict]:
    """
    Find the top-k knowledge articles most similar to `query`.
    Uses keyword matching on title, keywords, category, and content fields.
    Returns a list of dicts with article_number, title, category, score.
    """
    terms = query.lower().split()

    # Build OR conditions for each term across searchable fields
    conditions = []
    for term in terms:
        pattern = f"%{term}%"
        conditions.append(KnowledgeArticle.title.ilike(pattern))
        conditions.append(KnowledgeArticle.keywords.ilike(pattern))
        conditions.append(KnowledgeArticle.category.ilike(pattern))
        conditions.append(KnowledgeArticle.content.ilike(pattern))

    if conditions:
        articles = (
            db.query(KnowledgeArticle)
            .filter(or_(*conditions))
            .limit(k)
            .all()
        )
    else:
        articles = db.query(KnowledgeArticle).limit(k).all()

    results = []
    for article in articles:
        # Simple relevance score based on how many terms match
        score = 0.0
        text_blob = f"{article.title} {article.keywords} {article.category} {article.content or ''}".lower()
        for term in terms:
            if term in text_blob:
                score += 1.0
        score = min(score / max(len(terms), 1), 1.0)

        results.append({
            "article_number": article.article_number,
            "title": article.title,
            "category": article.category or "",
            "score": round(score, 2),
        })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def update_embedding(article_id: int, content: str, db: Session) -> None:
    """No-op for SQLite mode — embeddings are not stored."""
    pass
