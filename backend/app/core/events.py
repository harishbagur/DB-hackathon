"""
WebSocket connection manager.

Keeps track of active connections per incident room.
Agents broadcast events here; the frontend receives them in real time.
"""
from typing import Dict, List
from fastapi import WebSocket
import json


class ConnectionManager:
    def __init__(self):
        # incident_id → list of active WebSocket connections
        self._connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, incident_id: int):
        await websocket.accept()
        self._connections.setdefault(incident_id, []).append(websocket)

    def disconnect(self, websocket: WebSocket, incident_id: int):
        conns = self._connections.get(incident_id, [])
        if websocket in conns:
            conns.remove(websocket)

    async def broadcast(self, incident_id: int, event: dict):
        """Send a JSON event to every client watching this incident."""
        conns = self._connections.get(incident_id, [])
        dead = []
        for ws in conns:
            try:
                await ws.send_text(json.dumps(event))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, incident_id)


# Single instance shared across the app
manager = ConnectionManager()
