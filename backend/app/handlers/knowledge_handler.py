from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.models.knowledge import KnowledgeArticle
from app.core import similarity
from app.schemas.knowledge import ArticleResponse, ArticleSearchResult


def list_articles(db: Session) -> List[ArticleResponse]:
    articles = (
        db.query(KnowledgeArticle)
        .order_by(KnowledgeArticle.updated_date.desc())
        .all()
    )
    return [ArticleResponse.model_validate(a) for a in articles]


def search_articles(query: str, db: Session) -> List[ArticleSearchResult]:
    results = similarity.search(query, db, k=10)
    return [ArticleSearchResult(**r) for r in results]


def approve_article(article_id: int, db: Session) -> ArticleResponse:
    article = db.query(KnowledgeArticle).filter(
        KnowledgeArticle.article_id == article_id
    ).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    if article.status == "approved":
        raise HTTPException(status_code=400, detail="Article is already approved")

    article.status = "approved"
    article.updated_date = date.today()
    db.commit()
    db.refresh(article)

    # Generate embedding now that it's approved and searchable
    if article.content:
        similarity.update_embedding(article.article_id, article.content, db)

    return ArticleResponse.model_validate(article)
