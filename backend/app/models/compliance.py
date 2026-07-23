from sqlalchemy import Column, Integer, Numeric, Boolean
from app.database import Base


class DoraCompliance(Base):
    __tablename__ = "dora_compliance"

    compliance_id          = Column(Integer, primary_key=True, autoincrement=True)
    operational_resilience = Column(Numeric(5, 2))
    ict_risk               = Column(Numeric(5, 2))
    incident_management    = Column(Numeric(5, 2))
    business_continuity    = Column(Numeric(5, 2))
    third_party_risk       = Column(Numeric(5, 2))
    overall_score          = Column(Numeric(5, 2))
    audit_ready            = Column(Boolean)
