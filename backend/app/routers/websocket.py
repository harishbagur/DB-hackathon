"""
WebSocket endpoint — real-time chat room events.

The frontend connects here and receives every event broadcast by agents:
  - article_list       (listener agent opens the room)
  - text               (agent or user message)
  - system             (join/leave, diagnostics started)
  - approval_request   (agent proposes a Tier 2 action)
  - approval_response  (human approves or declines)
  - member_joined      (person added via +)

Connect from the frontend:
  const ws = new WebSocket("ws://localhost:8000/ws/incidents/1");
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.events import manager

router = APIRouter()


@router.websocket("/ws/incidents/{incident_id}")
async def websocket_endpoint(websocket: WebSocket, incident_id: int):
    await manager.connect(websocket, incident_id)
    try:
        while True:
            # Keep the connection alive.
            # The frontend can send a ping; we echo it back.
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, incident_id)
