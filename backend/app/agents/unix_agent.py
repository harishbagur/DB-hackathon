"""
Unix Agent — operates in two modes:

  Mode 1 (execute): Called by Healer Agent to run a specific playbook script.
                    No reasoning, just execution.

  Mode 2 (diagnose): Added to the chat room by the user via the + button.
                     Collects live diagnostics, asks Claude to analyze,
                     proposes a fix. Tier 2+ actions require Approve in chat.
"""
import json
from sqlalchemy.orm import Session

from app.agents.base_agent import BaseAgent
from app.core.state import IncidentState
from app.core import guardrails
from app.core.events import manager
from app.models.chat import ChatRoom, ChatMessage
from app.models.incident import Incident
from app.executors.unix_executor import UnixExecutor

import asyncio


DIAGNOSE_SYSTEM_PROMPT = """
You are a Unix platform agent for a bank's IT operations system.
You have been given an incident, its state, and live diagnostic output from the server.

Analyze the diagnostics and return your findings.

Respond with JSON in exactly this format:
{
  "hypothesis": "what you believe is the root cause",
  "proposed_fix": "the command or action to fix it",
  "action_tier": 0 or 1 or 2,
  "reasoning": "one sentence"
}

Action tiers:
  0 = read-only (no approval needed)
  1 = low-risk reversible (auto-execute, notify after)
  2 = config change or critical CI (needs human approval in chat)
"""


class UnixAgent(BaseAgent):

    # ------------------------------------------------------------------ #
    # Mode 2: User added this agent to the chat room                       #
    # ------------------------------------------------------------------ #
    def diagnose(self, incident: Incident, state: IncidentState, room_id: int, db: Session):
        executor = UnixExecutor()

        # Collect diagnostics (Tier 0 — always allowed)
        diagnostics = {
            "disk_usage": executor.run("df -h"),
            "service_status": executor.run("systemctl list-units --failed --no-pager"),
            "recent_logs": executor.run("journalctl -n 50 --no-pager"),
            "memory": executor.run("free -h"),
        }
        state.diagnostics_collected = list(diagnostics.keys())

        # Post a "collecting diagnostics" system message
        self._post_message(
            room_id=room_id,
            content="Joined the room. Collecting diagnostics: disk, services, logs, memory.",
            message_type="system",
            incident_id=incident.incident_id,
            db=db,
        )

        # Ask Claude to analyze
        result = self.call_claude(
            system=DIAGNOSE_SYSTEM_PROMPT,
            user=(
                f"Incident: {incident.title}\n"
                f"Description: {incident.description}\n"
                f"Prior actions attempted: {[a.action for a in state.actions_attempted]}\n"
                f"Diagnostics:\n{json.dumps(diagnostics, indent=2)}"
            ),
        )

        state.hypothesis = result["hypothesis"]
        action_tier = result["action_tier"]
        proposed_fix = result["proposed_fix"]

        # Check guardrails
        guard = guardrails.check(state, action_tier)

        if guard.allowed:
            # Auto-execute Tier 0/1
            content = (
                f"**Diagnosis:** {result['hypothesis']}\n\n"
                f"**Proposed fix:** `{proposed_fix}`\n"
                f"Tier {action_tier} — executing automatically."
            )
            self._post_message(room_id, content, "text", incident.incident_id, db)
            output = executor.run(proposed_fix)
            state.log_action("unix_agent", proposed_fix, action_tier, "executed", output[:200])
            self._post_message(room_id, f"Done. Output: `{output[:300]}`", "system",
                               incident.incident_id, db)
        else:
            # Tier 2 — post approval request in the chat
            content = (
                f"**Diagnosis:** {result['hypothesis']}\n\n"
                f"**Proposed fix:** `{proposed_fix}`\n\n"
                f"This is a Tier {action_tier} action ({guard.reason}). "
                f"Please Approve or Decline."
            )
            self._post_message(
                room_id=room_id,
                content=content,
                message_type="approval_request",
                incident_id=incident.incident_id,
                db=db,
                metadata={"proposed_fix": proposed_fix, "action_tier": action_tier},
            )

        db.commit()
        return state

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #
    def _post_message(self, room_id, content, message_type, incident_id, db,
                      metadata: dict = None):
        msg = ChatMessage(
            room_id=room_id,
            sender_type="agent",
            sender_id=4,          # Unix Agent is agent_id 4 in seed data
            sender_name="Unix Agent",
            content=content,
            message_type=message_type,
            metadata_json=json.dumps(metadata) if metadata else None,
        )
        db.add(msg)
        db.flush()

        event = {
            "type": message_type,
            "from": "unix_agent",
            "content": content,
            "metadata": metadata,
            "message_id": msg.message_id,
        }
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(manager.broadcast(incident_id, event))
        except Exception:
            pass

    def mock_response(self) -> dict:
        return {
            "hypothesis": "Mock: /var filesystem at 100%, preventing PID file creation.",
            "proposed_fix": "find /var/log -name '*.log' -mtime +7 -exec gzip {} \\;",
            "action_tier": 1,
            "reasoning": "Mock: disk full pattern detected in df output.",
        }
