from sqlalchemy import Column, Integer, String, Text, Date
from app.database import Base


class KnowledgeArticle(Base):
    __tablename__ = "knowledge_article"

    # Original columns
    article_id         = Column(Integer, primary_key=True, autoincrement=True)
    article_number     = Column(String(30))
    title              = Column(String(200))
    category           = Column(String(100))
    keywords           = Column(Text)
    helpful_percentage = Column(Integer)
    updated_date       = Column(Date)

    # Added in migration 002
    content            = Column(Text, nullable=True)
    status             = Column(String(20), default="approved")  # approved / draft
    source_incident_id = Column(Integer, nullable=True)
    # embedding column removed — using keyword search for SQLite compatibility
