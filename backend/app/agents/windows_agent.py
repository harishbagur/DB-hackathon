"""
Windows Agent — same interface as UnixAgent, stub implementation.

For the demo, this uses the WindowsExecutor which returns mock output.
In production, wire it to WinRM or a Windows management endpoint.
"""
import json
from sqlalchemy.orm import Session

from app.agents.base_agent import BaseAgent
from app.core.state import IncidentState
from app.core import guardrails
from app.core.events import manager
from app.models.chat import ChatMessage
from app.models.incident import Incident
from app.executors.windows_executor import WindowsExecutor

import asyncio


DIAGNOSE_SYSTEM_PROMPT = """
You are a Windows platform agent for a bank's IT operations system.
Analyze the diagnostic output and propose a fix.

Respond with JSON:
{
  "hypothesis": "root cause",
  "proposed_fix": "PowerShell command or action",
  "action_tier": 0 or 1 or 2,
  "reasoning": "one sentence"
}
"""


class WindowsAgent(BaseAgent):

    def diagnose(self, incident: Incident, state: IncidentState, room_id: int, db: Session):
        executor = WindowsExecutor()

        diagnostics = {
            "disk": executor.run("Get-PSDrive -PSProvider FileSystem | Select-Object Name,Used,Free"),
            "services": executor.run("Get-Service | Where-Object {$_.Status -eq 'Stopped'}"),
            "event_log": executor.run("Get-EventLog -LogName System -Newest 20 | Format-List"),
        }
        state.diagnostics_collected = list(diagnostics.keys())

        self._post_message(room_id, "Joined the room. Collecting Windows diagnostics.",
                           "system", incident.incident_id, db)

        result = self.call_claude(
            system=DIAGNOSE_SYSTEM_PROMPT,
            user=(
                f"Incident: {incident.title}\n"
                f"Description: {incident.description}\n"
                f"Diagnostics:\n{json.dumps(diagnostics, indent=2)}"
            ),
        )

        state.hypothesis = result["hypothesis"]
        action_tier = result["action_tier"]
        proposed_fix = result["proposed_fix"]
        guard = guardrails.check(state, action_tier)

        if guard.allowed:
            output = executor.run(proposed_fix)
            state.log_action("windows_agent", proposed_fix, action_tier, "executed", output[:200])
            self._post_message(room_id,
                               f"**Fix applied:** `{proposed_fix}`\nOutput: `{output[:300]}`",
                               "system", incident.incident_id, db)
        else:
            self._post_message(
                room_id=room_id,
                content=(f"**Diagnosis:** {result['hypothesis']}\n\n"
                         f"**Proposed fix:** `{proposed_fix}`\n\n"
                         f"Tier {action_tier} — needs approval. {guard.reason}"),
                message_type="approval_request",
                incident_id=incident.incident_id,
                db=db,
                metadata={"proposed_fix": proposed_fix, "action_tier": action_tier},
            )

        db.commit()
        return state

    def _post_message(self, room_id, content, message_type, incident_id, db, metadata=None):
        msg = ChatMessage(
            room_id=room_id,
            sender_type="agent",
            sender_id=5,          # Windows Agent is agent_id 5 in seed data
            sender_name="Windows Agent",
            content=content,
            message_type=message_type,
            metadata_json=json.dumps(metadata) if metadata else None,
        )
        db.add(msg)
        db.flush()

        event = {"type": message_type, "from": "windows_agent",
                 "content": content, "metadata": metadata}
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(manager.broadcast(incident_id, event))
        except Exception:
            pass

    def mock_response(self) -> dict:
        return {
            "hypothesis": "Mock: DNS Client service stopped after Windows update.",
            "proposed_fix": "net start 'DNS Client'",
            "action_tier": 1,
            "reasoning": "Mock: DNS failure pattern in event log.",
        }
