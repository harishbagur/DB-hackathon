from sqlalchemy import Column, Integer, String, Numeric
from app.database import Base


class AIAgent(Base):
    __tablename__ = "ai_agent"

    agent_id         = Column(Integer, primary_key=True, autoincrement=True)
    agent_name       = Column(String(100))
    agent_type       = Column(String(50))
    status           = Column(String(20))        # Idle / Running / Completed / Error
    confidence_score = Column(Numeric(5, 2))
