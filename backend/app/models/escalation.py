from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.database import Base


class Escalation(Base):
    __tablename__ = "escalation"

    escalation_id  = Column(Integer, primary_key=True, autoincrement=True)
    incident_id    = Column(Integer, ForeignKey("incident.incident_id"))
    assigned_team  = Column(String(100))
    engineer_name  = Column(String(100))
    reason         = Column(Text)
    estimated_wait = Column(Integer)       # minutes
    status         = Column(String(50))    # Pending / Acknowledged / Resolved
