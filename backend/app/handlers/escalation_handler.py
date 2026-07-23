from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.escalation import Escalation
from app.models.user import User


def get_escalation(incident_id: int, db: Session) -> dict:
    esc = db.query(Escalation).filter(Escalation.incident_id == incident_id).first()
    if not esc:
        raise HTTPException(status_code=404, detail="No escalation record for this incident")
    return {
        "escalation_id": esc.escalation_id,
        "incident_id": esc.incident_id,
        "assigned_team": esc.assigned_team,
        "engineer_name": esc.engineer_name,
        "reason": esc.reason,
        "estimated_wait": esc.estimated_wait,
        "status": esc.status,
    }


def update_status(escalation_id: int, status: str, db: Session) -> dict:
    esc = db.query(Escalation).filter(Escalation.escalation_id == escalation_id).first()
    if not esc:
        raise HTTPException(status_code=404, detail="Escalation not found")

    valid_statuses = ("Pending", "Acknowledged", "Resolved")
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of {valid_statuses}")

    esc.status = status
    db.commit()
    return {"escalation_id": escalation_id, "status": status}


def get_assignment_group(incident_id: int, db: Session) -> list:
    """
    Return the list of users in the assignment group for this incident.
    Used by the chat room + button to populate the people picker.
    In production this would query ServiceNow's assignment group.
    For the demo we return all users.
    """
    users = db.query(User).all()
    return [
        {
            "user_id": u.user_id,
            "full_name": u.full_name,
            "role": u.role,
            "department": u.department,
            "location": u.location,
        }
        for u in users
    ]
