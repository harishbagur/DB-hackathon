from pydantic import BaseModel
from typing import Optional
from datetime import date


class ExecutiveMetricsResponse(BaseModel):
    metric_date: Optional[date]
    automated_resolution: Optional[float]
    manual_escalation: Optional[float]
    avg_resolution_minutes: Optional[int]
    critical_incidents: Optional[int]
    dora_score: Optional[float]
    cyber_hygiene_score: Optional[float]

    class Config:
        from_attributes = True


class DoraResponse(BaseModel):
    operational_resilience: Optional[float]
    ict_risk: Optional[float]
    incident_management: Optional[float]
    business_continuity: Optional[float]
    third_party_risk: Optional[float]
    overall_score: Optional[float]
    audit_ready: Optional[bool]

    class Config:
        from_attributes = True
