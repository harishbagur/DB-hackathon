from sqlalchemy import Column, Integer, Numeric, Date
from app.database import Base


class ExecutiveMetrics(Base):
    __tablename__ = "executive_metrics"

    metric_id              = Column(Integer, primary_key=True, autoincrement=True)
    metric_date            = Column(Date)
    automated_resolution   = Column(Numeric(5, 2))   # percentage
    manual_escalation      = Column(Numeric(5, 2))   # percentage
    avg_resolution_minutes = Column(Integer)
    critical_incidents     = Column(Integer)
    dora_score             = Column(Numeric(5, 2))
    cyber_hygiene_score    = Column(Numeric(5, 2))
