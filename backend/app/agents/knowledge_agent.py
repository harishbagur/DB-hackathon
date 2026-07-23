"""
Knowledge Agent

Turns every successful resolution into a draft KB article.
Checks for near-duplicates before creating a new one.
Human must approve before the article publishes.
"""
import json
from datetime import date
from sqlalchemy.orm import Session

from app.agents.base_agent import BaseAgent
from app.core.state import IncidentState
from app.core import similarity
from app.models.knowledge import KnowledgeArticle
from app.models.incident import Incident


SYSTEM_PROMPT = """
You are a Knowledge Management Agent for a bank's IT operations system.
You are given an incident and its resolution thread.
Draft a clear, reusable KB article so future incidents resolve faster.

Respond with JSON in exactly this format:
{
  "title": "concise article title",
  "category": "category name",
  "keywords": "comma-separated keywords",
  "content": "step-by-step resolution. Use plain text, no markdown."
}
"""


class KnowledgeAgent(BaseAgent):

    def run(self, incident: Incident, state: IncidentState,
            resolution_summary: str, db: Session) -> KnowledgeArticle | None:

        result = self.call_claude(
            system=SYSTEM_PROMPT,
            user=(
                f"Incident: {incident.title}\n"
                f"Description: {incident.description}\n"
                f"Platform: {state.platform}\n"
                f"Resolution: {resolution_summary}\n"
                f"Actions taken: {[a.action for a in state.actions_attempted]}"
            ),
        )

        # Check for near-duplicate using pgvector
        similar = similarity.search(result["title"] + " " + result["content"], db, k=1)
        if similar and similar[0]["score"] > 0.90:
            # Update the existing article rather than creating a duplicate
            existing = (
                db.query(KnowledgeArticle)
                .filter(KnowledgeArticle.article_number == similar[0]["article_number"])
                .first()
            )
            if existing:
                existing.content = result["content"]
                existing.keywords = result["keywords"]
                existing.updated_date = date.today()
                db.commit()
                similarity.update_embedding(existing.article_id, result["content"], db)
                return existing

        # Create new draft article
        # Generate article number: KB-{incident_number}
        article_number = f"KB-{incident.incident_number}"
        article = KnowledgeArticle(
            article_number=article_number,
            title=result["title"],
            category=result["category"],
            keywords=result["keywords"],
            content=result["content"],
            helpful_percentage=0,
            updated_date=date.today(),
            status="draft",                          # human approves before publish
            source_incident_id=incident.incident_id,
        )
        db.add(article)
        db.commit()
        db.refresh(article)

        # Generate and store embedding so it's searchable immediately after approval
        similarity.update_embedding(article.article_id, result["content"], db)
        return article

    def mock_response(self) -> dict:
        return {
            "title": "VPN Authentication Failure After Security Patch",
            "category": "VPN",
            "keywords": "VPN,authentication,patch,service restart",
            "content": (
                "1. Identify the failing service using: systemctl list-units --failed\n"
                "2. Restart the authentication service: sudo systemctl restart auth-service\n"
                "3. Validate VPN connectivity for 5 users before confirming resolution.\n"
                "4. If issue persists, roll back the patch using the change management portal."
            ),
        }
