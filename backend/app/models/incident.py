from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Numeric
from app.database import Base


class Incident(Base):
    __tablename__ = "incident"

    # Original columns
    incident_id   = Column(Integer, primary_key=True, autoincrement=True)
    incident_number = Column(String(30))
    title         = Column(String(200))
    description   = Column(Text)
    priority      = Column(String(20))       # Critical / High / Medium / Low
    status        = Column(String(30))       # Investigating / Resolved / Closed
    affected_users = Column(Integer)
    application   = Column(String(100))
    root_cause    = Column(String(200))
    created_by    = Column(Integer, ForeignKey("app_user.user_id"))
    created_at    = Column(TIMESTAMP)
    resolved_at   = Column(TIMESTAMP, nullable=True)

    # Added in migration 002 — agent state tracking
    platform                  = Column(String(20), default="unix")    # unix / windows
    ci_criticality            = Column(String(20), default="tier2")   # tier0–tier3
    classification            = Column(String(20), default="unknown") # real / false / unknown
    classification_confidence = Column(Numeric(5, 2), default=0)
    hop_count                 = Column(Integer, default=0)
    current_owner             = Column(String(50), default="incident_lead_agent")
