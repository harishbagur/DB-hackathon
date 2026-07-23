from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.handlers import chat_handler
from app.schemas.chat import (
    ChatRoomResponse, MessageResponse,
    SendMessageRequest, AddAgentRequest,
    AddMemberRequest, ApprovalRequest,
)

router = APIRouter()


@router.get("/{incident_id}/room", response_model=ChatRoomResponse)
def get_room(incident_id: int, db: Session = Depends(get_db)):
    """Get the chat room for an incident — all messages, agents, and members."""
    return chat_handler.get_room(incident_id, db)


@router.post("/{incident_id}/room/agents")
def add_agent(incident_id: int, req: AddAgentRequest, db: Session = Depends(get_db)):
    """
    User clicks + on the agent bar and picks an agent.
    The agent joins the room and immediately starts diagnosing.
    """
    return chat_handler.add_agent(incident_id, req.agent_id, db)


@router.post("/{incident_id}/room/members")
def add_member(incident_id: int, req: AddMemberRequest, db: Session = Depends(get_db)):
    """User clicks + on the people row and picks a colleague."""
    return chat_handler.add_member(incident_id, req.user_id, db)


@router.post("/{incident_id}/room/messages", response_model=MessageResponse)
def send_message(incident_id: int, req: SendMessageRequest, db: Session = Depends(get_db)):
    """Send a message from a human user into the room."""
    return chat_handler.send_message(incident_id, req.user_id, req.content, db)


@router.post("/{incident_id}/room/approve")
def handle_approval(incident_id: int, req: ApprovalRequest, db: Session = Depends(get_db)):
    """
    Approve or decline a Tier 2 action proposed by an agent.
    Approved → executes immediately. Declined → logged, no action taken.
    """
    return chat_handler.handle_approval(incident_id, req, db)


@router.get("/{incident_id}/escalation/group")
def get_assignment_group(incident_id: int, db: Session = Depends(get_db)):
    """
    Return the people picker list for the + button on the people row.
    In production: queries ServiceNow assignment group.
    """
    from app.handlers import escalation_handler
    return escalation_handler.get_assignment_group(incident_id, db)
