from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class IncidentResponse(BaseModel):
    incident_id: int
    incident_number: str
    title: str
    description: str
    priority: str
    status: str
    affected_users: Optional[int]
    application: Optional[str]
    platform: Optional[str]
    ci_criticality: Optional[str]
    classification: Optional[str]
    classification_confidence: Optional[float]
    hop_count: Optional[int]
    current_owner: Optional[str]
    created_at: Optional[datetime]
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


class TriageResponse(BaseModel):
    incident_id: int
    classification: str
    confidence: float
    resolution: Optional[str]
    current_owner: str
    hop_count: int
    message: str
