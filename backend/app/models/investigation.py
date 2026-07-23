from sqlalchemy import Column, Integer, Text, ForeignKey
from app.database import Base


class AIInvestigation(Base):
    __tablename__ = "ai_investigation"

    investigation_id = Column(Integer, primary_key=True, autoincrement=True)
    incident_id      = Column(Integer, ForeignKey("incident.incident_id"))
    agent_id         = Column(Integer, ForeignKey("ai_agent.agent_id"))
    findings         = Column(Text)
    recommendation   = Column(Text)
    execution_time   = Column(Integer)    # seconds
