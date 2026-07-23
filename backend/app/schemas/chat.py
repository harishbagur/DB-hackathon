from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MessageResponse(BaseModel):
    message_id: int
    sender_type: str
    sender_name: str
    content: str
    message_type: str
    metadata_json: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class ChatRoomResponse(BaseModel):
    room_id: int
    incident_id: int
    status: str
    messages: List[MessageResponse] = []
    agent_names: List[str] = []
    member_names: List[str] = []


class SendMessageRequest(BaseModel):
    user_id: int
    content: str


class AddAgentRequest(BaseModel):
    agent_id: int


class AddMemberRequest(BaseModel):
    user_id: int


class ApprovalRequest(BaseModel):
    message_id: int
    approved: bool
    user_id: int
