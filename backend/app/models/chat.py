from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, func
from app.database import Base


class ChatRoom(Base):
    """One room per incident. Created when the listener agent fires."""
    __tablename__ = "chat_room"

    room_id     = Column(Integer, primary_key=True, autoincrement=True)
    incident_id = Column(Integer, ForeignKey("incident.incident_id"), unique=True)
    status      = Column(String(20), default="open")   # open / resolved / closed
    created_at  = Column(TIMESTAMP, server_default=func.now())


class ChatMessage(Base):
    """Every message in the room — from agents or people."""
    __tablename__ = "chat_message"

    message_id    = Column(Integer, primary_key=True, autoincrement=True)
    room_id       = Column(Integer, ForeignKey("chat_room.room_id"))
    sender_type   = Column(String(10))      # agent / user
    sender_id     = Column(Integer)         # agent_id or user_id
    sender_name   = Column(String(100))
    content       = Column(Text)
    message_type  = Column(String(30), default="text")
    # text / article_list / approval_request / system / approval_response
    metadata_json = Column(Text, nullable=True)  # JSON for structured messages
    created_at    = Column(TIMESTAMP, server_default=func.now())


class RoomAgent(Base):
    """Tracks which AI agents have been added to a room by the user."""
    __tablename__ = "room_agent"

    id       = Column(Integer, primary_key=True, autoincrement=True)
    room_id  = Column(Integer, ForeignKey("chat_room.room_id"))
    agent_id = Column(Integer, ForeignKey("ai_agent.agent_id"))
    added_at = Column(TIMESTAMP, server_default=func.now())


class RoomMember(Base):
    """Tracks which human users have been added to a room."""
    __tablename__ = "room_member"

    id       = Column(Integer, primary_key=True, autoincrement=True)
    room_id  = Column(Integer, ForeignKey("chat_room.room_id"))
    user_id  = Column(Integer, ForeignKey("app_user.user_id"))
    added_at = Column(TIMESTAMP, server_default=func.now())
