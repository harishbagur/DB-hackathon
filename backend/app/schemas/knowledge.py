from pydantic import BaseModel
from typing import Optional
from datetime import date


class ArticleResponse(BaseModel):
    article_id: int
    article_number: str
    title: str
    category: Optional[str]
    keywords: Optional[str]
    content: Optional[str]
    helpful_percentage: Optional[int]
    status: Optional[str]
    updated_date: Optional[date]

    class Config:
        from_attributes = True


class ArticleSearchResult(BaseModel):
    article_number: str
    title: str
    category: str
    score: float
