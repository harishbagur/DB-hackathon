from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.handlers import knowledge_handler
from app.schemas.knowledge import ArticleResponse, ArticleSearchResult

router = APIRouter()


@router.get("/", response_model=List[ArticleResponse])
def list_articles(db: Session = Depends(get_db)):
    """List all knowledge articles."""
    return knowledge_handler.list_articles(db)


@router.get("/search", response_model=List[ArticleSearchResult])
def search_articles(q: str = Query(..., description="Search query"), db: Session = Depends(get_db)):
    """
    Semantic search over the knowledge base using pgvector.
    Returns top 10 articles ranked by cosine similarity.
    """
    return knowledge_handler.search_articles(q, db)


@router.patch("/{article_id}/approve", response_model=ArticleResponse)
def approve_article(article_id: int, db: Session = Depends(get_db)):
    """
    Approve a draft KB article created by the Knowledge Agent.
    Once approved it becomes searchable in the listener agent's results.
    """
    return knowledge_handler.approve_article(article_id, db)
