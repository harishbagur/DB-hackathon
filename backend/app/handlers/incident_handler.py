from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.agents.incident_lead_agent import IncidentLeadAgent
from app.schemas.incident import IncidentResponse, TriageResponse


def list_incidents(db: Session) -> List[IncidentResponse]:
    incidents = db.query(Incident).order_by(Incident.created_at.desc()).all()
    return [IncidentResponse.model_validate(i) for i in incidents]


def get_incident(incident_id: int, db: Session) -> IncidentResponse:
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentResponse.model_validate(incident)


def trigger_triage(incident_id: int, db: Session) -> TriageResponse:
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if incident.status in ("Resolved", "Closed"):
        raise HTTPException(status_code=400, detail="Incident is already resolved or closed")

    state = IncidentLeadAgent().run(incident, db)

    return TriageResponse(
        incident_id=incident.incident_id,
        classification=state.classification,
        confidence=state.classification_confidence,
        resolution=state.resolution,
        current_owner=state.current_owner,
        hop_count=state.hop_count,
        message=_summary_message(state),
    )


def _summary_message(state) -> str:
    if state.resolution == "false_positive_handled":
        return "Incident classified as false positive and handled."
    if state.resolution and "self_healed" in state.resolution:
        return f"Incident self-healed via {state.resolution}."
    if state.current_owner == "listener_agent":
        return "Healer could not resolve. Chat room opened with top articles."
    if state.escalation_reason:
        return f"Escalated: {state.escalation_reason}"
    return "Triage complete."
