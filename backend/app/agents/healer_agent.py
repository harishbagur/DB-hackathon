"""
Healer Agent

Responsibilities:
  1. Load playbooks for the incident's platform
  2. Ask Claude to find the best matching playbook
  3. Only act if confidence >= HEALER_CONFIDENCE_THRESHOLD
  4. Dispatch execution to unix_agent or windows_agent
  5. Verify the fix actually worked
  6. Log the attempt (success or fail) to ai_investigation
"""
from sqlalchemy.orm import Session
from datetime import datetime

from app.agents.base_agent import BaseAgent
from app.core.state import IncidentState
from app.core import guardrails
from app.models.incident import Incident
from app.models.playbook import Playbook
from app.models.investigation import AIInvestigation
from app.models.agent import AIAgent
from app.config import settings


SYSTEM_PROMPT = """
You are the Healer Agent for a bank's IT operations system.
You are given an incident and a list of available playbooks.
Your job is to find the best matching playbook and rate your confidence.

Only match a playbook if you are highly confident it addresses the root cause.
When in doubt, return a low confidence score — it is safer to escalate.

Respond with JSON in exactly this format:
{
  "matched_playbook_name": "name or null",
  "confidence": 0.0 to 1.0,
  "reasoning": "one sentence",
  "service_name": "name of service if relevant, else null"
}
"""


class HealerAgent(BaseAgent):

    def run(self, incident: Incident, state: IncidentState, db: Session) -> IncidentState:
        # Load playbooks for this platform
        playbooks = (
            db.query(Playbook)
            .filter(Playbook.platform.in_([state.platform, "any"]))
            .all()
        )

        if not playbooks:
            state.log_action("healer_agent", "no_playbooks_available", 0, "skipped",
                             "No playbooks found for this platform")
            return state

        playbook_list = [
            {"name": p.name, "description": p.description, "keywords": p.trigger_keywords}
            for p in playbooks
        ]

        result = self.call_claude(
            system=SYSTEM_PROMPT,
            user=(
                f"Incident: {incident.title}\n"
                f"Description: {incident.description}\n"
                f"Platform: {state.platform}\n\n"
                f"Available playbooks:\n{playbook_list}"
            ),
        )

        confidence = result["confidence"]
        matched_name = result.get("matched_playbook_name")

        if confidence < settings.HEALER_CONFIDENCE_THRESHOLD or not matched_name:
            state.log_action("healer_agent", "no_high_confidence_match", 0, "skipped",
                             f"Best match confidence {confidence:.0%} below threshold")
            return state

        # Find the matched playbook
        matched = next((p for p in playbooks if p.name == matched_name), None)
        if not matched:
            return state

        # Guardrail check before executing
        guard = guardrails.check(state, matched.action_tier)
        if not guard.allowed:
            state.log_action("healer_agent", matched.name, matched.action_tier, "blocked",
                             guard.reason)
            return state

        # Execute via the right platform agent
        service_name = result.get("service_name") or "unknown"
        script = matched.script.replace("{service_name}", service_name)
        verify_cmd = matched.verify_command.replace("{service_name}", service_name)

        from app.executors.unix_executor import UnixExecutor
        from app.executors.windows_executor import WindowsExecutor
        executor = UnixExecutor() if state.platform == "unix" else WindowsExecutor()

        exec_output = executor.run(script)
        verify_output = executor.run(verify_cmd)
        success = executor.verify_success(verify_output)

        outcome = "success" if success else "failed"
        state.log_action("healer_agent", matched.name, matched.action_tier, outcome,
                         f"Script output: {exec_output[:200]}")

        # Update playbook stats
        if success:
            matched.success_count += 1
        else:
            matched.failure_count += 1

        # Log to ai_investigation
        agent_row = db.query(AIAgent).filter(AIAgent.agent_name == "Healer Agent").first()
        investigation = AIInvestigation(
            incident_id=incident.incident_id,
            agent_id=agent_row.agent_id if agent_row else None,
            findings=f"Matched playbook: {matched.name} (confidence {confidence:.0%})",
            recommendation=matched.description,
            execution_time=5,
        )
        db.add(investigation)

        if success:
            state.resolution = f"self_healed_via_{matched.name}"
            incident.status = "Resolved"
            incident.resolved_at = datetime.utcnow()

        db.commit()
        return state

    def mock_response(self) -> dict:
        return {
            "matched_playbook_name": "clear-disk-space",
            "confidence": 0.92,
            "reasoning": "Mock: disk full keywords match clear-disk-space playbook.",
            "service_name": None,
        }
