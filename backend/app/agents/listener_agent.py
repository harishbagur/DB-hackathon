"""
Listener Agent

Responsibilities:
  1. Search knowledge base using pgvector similarity
  2. Create the chat room for this incident
  3. Post the top-10 articles as the first message
  4. Broadcast to all WebSocket clients watching this incident
"""
import json
from sqlalchemy.orm import Session

from app.agents.base_agent import BaseAgent
from app.core.state import IncidentState, ArticleMatch
from app.core import similarity
from app.core.events import manager
from app.models.incident import Incident
from app.models.chat import ChatRoom, ChatMessage
from app.config import settings

import asyncio


class ListenerAgent(BaseAgent):

    def run(self, incident: Incident, state: IncidentState, db: Session) -> IncidentState:
        # --- Step 1: Search top-K articles ---
        query = f"{incident.title} {incident.description}"
        results = similarity.search(query, db, k=settings.SIMILARITY_TOP_K)

        # Always show top 10, whatever the scores — user decides what's relevant
        state.articles_shown = [
            ArticleMatch(
                id=r["article_number"],
                title=r["title"],
                score=r["score"],
                article_type="kb_article",
            )
            for r in results
        ]

        # --- Step 2: Create the chat room ---
        room = db.query(ChatRoom).filter(ChatRoom.incident_id == incident.incident_id).first()
        if not room:
            room = ChatRoom(incident_id=incident.incident_id, status="open")
            db.add(room)
            db.flush()   # get room_id before commit

        # --- Step 3: Post the article list as the opening message ---
        article_payload = [
            {"rank": i + 1, **a.__dict__}
            for i, a in enumerate(state.articles_shown)
        ]
        # Remove dataclass internal fields
        for a in article_payload:
            a.pop("__dataclass_fields__", None)

        message = ChatMessage(
            room_id=room.room_id,
            sender_type="agent",
            sender_id=3,          # Listener Agent is agent_id 3 in seed data
            sender_name="Listener Agent",
            content=(
                f"Here are the top {len(state.articles_shown)} related articles and incidents.\n"
                "Use any of these, or click + to add an agent or a colleague."
            ),
            message_type="article_list",
            metadata_json=json.dumps(article_payload),
        )
        db.add(message)
        db.commit()

        # --- Step 4: Broadcast to WebSocket clients ---
        event = {
            "type": "article_list",
            "from": "listener_agent",
            "room_id": room.room_id,
            "articles": article_payload,
            "content": message.content,
        }
        # Run broadcast in the event loop if one is running, else schedule it
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(manager.broadcast(incident.incident_id, event))
            else:
                loop.run_until_complete(manager.broadcast(incident.incident_id, event))
        except Exception:
            pass  # WebSocket broadcast is best-effort

        state.current_owner = "listener_agent"
        return state

    def mock_response(self) -> dict:
        # Listener agent doesn't call Claude — pgvector does the search
        return {}
