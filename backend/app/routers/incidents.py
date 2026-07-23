from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.handlers import incident_handler
from app.schemas.incident import IncidentResponse, TriageResponse

router = APIRouter()


@router.get("/", response_model=List[IncidentResponse])
def list_incidents(db: Session = Depends(get_db)):
    """List all incidents, newest first."""
    return incident_handler.list_incidents(db)


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """Get a single incident with its current agent state."""
    return incident_handler.get_incident(incident_id, db)


@router.post("/{incident_id}/triage", response_model=TriageResponse)
def trigger_triage(incident_id: int, db: Session = Depends(get_db)):
    """
    Trigger the full agent pipeline for an incident.
    Runs: Incident Lead → Healer → Listener (if needed).
    """
    return incident_handler.trigger_triage(incident_id, db)
