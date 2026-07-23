"""
Incident Lead Agent

Responsibilities:
  1. Classify incident as real or false positive (with confidence)
  2. Handle false positives according to confidence tier
  3. Route real incidents to the Healer Agent
  4. If healer fails, fire the Listener Agent
  5. Enforce hop count and time limits
"""
from sqlalchemy.orm import Session
from datetime import datetime

from app.agents.base_agent import BaseAgent
from app.core.state import IncidentState
from app.models.incident import Incident
from app.config import settings


SYSTEM_PROMPT = """
You are the Incident Lead Agent for a bank's IT operations system.
Your job is to classify incoming incidents as real or false positives.

A false positive is an alert that triggered but requires no action:
- The condition has already self-corrected
- It is a known noisy alert with no downstream impact
- Metrics returned to normal before anyone could act

Respond with JSON in exactly this format:
{
  "classification": "real" | "false",
  "confidence": 0.0 to 1.0,
  "reasoning": "one sentence explanation"
}
"""


class IncidentLeadAgent(BaseAgent):

    def run(self, incident: Incident, db: Session) -> IncidentState:
        state = IncidentState.from_incident(incident)

        # --- Step 1: Classify ---
        result = self.call_claude(
            system=SYSTEM_PROMPT,
            user=(
                f"Incident: {incident.title}\n"
                f"Description: {incident.description}\n"
                f"Application: {incident.application}\n"
                f"Priority: {incident.priority}\n"
                f"Affected users: {incident.affected_users}"
            ),
        )

        state.classification = result["classification"]
        state.classification_confidence = result["confidence"]

        # Persist classification back to the DB
        incident.classification = state.classification
        incident.classification_confidence = state.classification_confidence
        db.commit()

        # --- Step 2: Handle false positive ---
        if state.classification == "false":
            self._handle_false_positive(incident, state, db)
            return state

        # --- Step 3: Route to healer ---
        state.hop_count += 1
        incident.hop_count = state.hop_count
        incident.current_owner = "healer_agent"
        db.commit()

        from app.agents.healer_agent import HealerAgent
        state = HealerAgent().run(incident, state, db)

        # --- Step 4: If healer didn't resolve, fire listener ---
        if state.resolution is None and state.hop_count < settings.MAX_HOP_COUNT:
            state.hop_count += 1
            incident.hop_count = state.hop_count
            incident.current_owner = "listener_agent"
            db.commit()

            from app.agents.listener_agent import ListenerAgent
            state = ListenerAgent().run(incident, state, db)

        elif state.hop_count >= settings.MAX_HOP_COUNT:
            state.escalation_reason = f"Max hop count ({settings.MAX_HOP_COUNT}) reached"
            incident.status = "Escalated"
            db.commit()

        return state

    def _handle_false_positive(self, incident: Incident, state: IncidentState, db: Session):
        conf = state.classification_confidence

        if conf > 0.85:
            # High confidence — auto-close
            incident.status = "Closed"
            incident.resolved_at = datetime.utcnow()
            note = f"[Incident Lead Agent] Auto-closed as false positive (confidence: {conf:.0%}). Reason: {state.classification}"
        elif conf >= 0.60:
            # Medium confidence — downgrade, leave open
            incident.priority = "Low"
            note = f"[Incident Lead Agent] Downgraded to Low priority. Possible false positive (confidence: {conf:.0%}). Monitoring."
        else:
            # Low confidence — treat as real, routing will continue
            return

        incident.root_cause = note
        db.commit()
        state.resolution = "false_positive_handled"

    def mock_response(self) -> dict:
        return {
            "classification": "real",
            "confidence": 0.91,
            "reasoning": "Mock: incident description matches known failure pattern.",
        }
