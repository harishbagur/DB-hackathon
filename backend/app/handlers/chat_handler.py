import json
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.chat import ChatRoom, ChatMessage, RoomAgent, RoomMember
from app.models.incident import Incident
from app.models.agent import AIAgent
from app.models.user import User
from app.core.state import IncidentState
from app.core.events import manager
from app.schemas.chat import (
    ChatRoomResponse, MessageResponse, ApprovalRequest,
)

import asyncio


def get_room(incident_id: int, db: Session) -> ChatRoomResponse:
    room = db.query(ChatRoom).filter(ChatRoom.incident_id == incident_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="No chat room for this incident yet. Trigger triage first.")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.room_id == room.room_id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    room_agents = db.query(RoomAgent).filter(RoomAgent.room_id == room.room_id).all()
    room_members = db.query(RoomMember).filter(RoomMember.room_id == room.room_id).all()

    agent_names = []
    for ra in room_agents:
        agent = db.query(AIAgent).filter(AIAgent.agent_id == ra.agent_id).first()
        if agent:
            agent_names.append(agent.agent_name)

    member_names = []
    for rm in room_members:
        user = db.query(User).filter(User.user_id == rm.user_id).first()
        if user:
            member_names.append(user.full_name)

    return ChatRoomResponse(
        room_id=room.room_id,
        incident_id=room.incident_id,
        status=room.status,
        messages=[MessageResponse.model_validate(m) for m in messages],
        agent_names=["Listener Agent"] + agent_names,
        member_names=member_names,
    )


def add_agent(incident_id: int, agent_id: int, db: Session) -> dict:
    """User clicks + and picks an agent (unix or windows)."""
    room = _get_room_or_404(incident_id, db)
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    agent = db.query(AIAgent).filter(AIAgent.agent_id == agent_id).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Prevent duplicate additions
    already = db.query(RoomAgent).filter(
        RoomAgent.room_id == room.room_id,
        RoomAgent.agent_id == agent_id,
    ).first()
    if not already:
        db.add(RoomAgent(room_id=room.room_id, agent_id=agent_id))
        db.commit()

    # Build state from incident and trigger agent diagnosis
    state = IncidentState.from_incident(incident)

    if "unix" in agent.agent_name.lower():
        from app.agents.unix_agent import UnixAgent
        UnixAgent().diagnose(incident, state, room.room_id, db)
    elif "windows" in agent.agent_name.lower():
        from app.agents.windows_agent import WindowsAgent
        WindowsAgent().diagnose(incident, state, room.room_id, db)

    return {"message": f"{agent.agent_name} added and diagnosis started.", "room_id": room.room_id}


def add_member(incident_id: int, user_id: int, db: Session) -> dict:
    """User clicks + and picks a person from the assignment group."""
    room = _get_room_or_404(incident_id, db)
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    already = db.query(RoomMember).filter(
        RoomMember.room_id == room.room_id,
        RoomMember.user_id == user_id,
    ).first()
    if not already:
        db.add(RoomMember(room_id=room.room_id, user_id=user_id))
        db.commit()

    # System message announcing the join
    msg = ChatMessage(
        room_id=room.room_id,
        sender_type="user",
        sender_id=user_id,
        sender_name=user.full_name,
        content=f"{user.full_name} joined the room.",
        message_type="system",
    )
    db.add(msg)
    db.commit()

    _broadcast_sync(incident_id, {"type": "member_joined", "name": user.full_name})
    return {"message": f"{user.full_name} added to room.", "room_id": room.room_id}


def send_message(incident_id: int, user_id: int, content: str, db: Session) -> MessageResponse:
    room = _get_room_or_404(incident_id, db)
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    msg = ChatMessage(
        room_id=room.room_id,
        sender_type="user",
        sender_id=user_id,
        sender_name=user.full_name,
        content=content,
        message_type="text",
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    _broadcast_sync(incident_id, {
        "type": "text",
        "from": user.full_name,
        "content": content,
        "message_id": msg.message_id,
    })
    return MessageResponse.model_validate(msg)


def handle_approval(incident_id: int, req: ApprovalRequest, db: Session) -> dict:
    """User approves or declines a Tier 2 action from an agent."""
    room = _get_room_or_404(incident_id, db)
    original_msg = db.query(ChatMessage).filter(
        ChatMessage.message_id == req.message_id
    ).first()
    if not original_msg or original_msg.message_type != "approval_request":
        raise HTTPException(status_code=404, detail="Approval request not found")

    meta = json.loads(original_msg.metadata_json or "{}")
    proposed_fix = meta.get("proposed_fix", "")
    user = db.query(User).filter(User.user_id == req.user_id).first()
    user_name = user.full_name if user else "Unknown"

    if req.approved:
        # Execute the approved fix
        incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
        from app.executors.unix_executor import UnixExecutor
        from app.executors.windows_executor import WindowsExecutor
        executor = UnixExecutor() if incident.platform == "unix" else WindowsExecutor()
        output = executor.run(proposed_fix)
        response_content = f"✅ **Approved by {user_name}**\nExecuted: `{proposed_fix}`\nOutput: `{output[:300]}`"
    else:
        response_content = f"❌ **Declined by {user_name}**. Action not taken."

    response_msg = ChatMessage(
        room_id=room.room_id,
        sender_type="user",
        sender_id=req.user_id,
        sender_name=user_name,
        content=response_content,
        message_type="approval_response",
    )
    db.add(response_msg)
    db.commit()

    _broadcast_sync(incident_id, {"type": "approval_response", "content": response_content})
    return {"approved": req.approved, "message": response_content}


# ------------------------------------------------------------------ #
# Helpers                                                              #
# ------------------------------------------------------------------ #

def _get_room_or_404(incident_id: int, db: Session) -> ChatRoom:
    room = db.query(ChatRoom).filter(ChatRoom.incident_id == incident_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="No chat room for this incident")
    return room


def _broadcast_sync(incident_id: int, event: dict):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(manager.broadcast(incident_id, event))
    except Exception:
        pass
