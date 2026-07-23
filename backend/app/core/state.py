"""
IncidentState — the shared record every agent reads and writes.
Travels with the incident through every handoff so no context is lost.
Newly added agents/people inherit the full state when they join the room.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import datetime
import json


@dataclass
class ActionAttempt:
    agent: str
    action: str
    tier: int
    outcome: str          # success / failed / skipped
    detail: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class ArticleMatch:
    id: str               # article_number e.g. KB-12451 or INC548239
    title: str
    score: float          # 0.0 – 1.0, cosine similarity from pgvector
    article_type: str     # kb_article / incident


@dataclass
class IncidentState:
    incident_id: int
    incident_number: str
    platform: str                   # unix / windows
    ci_criticality: str             # tier0 / tier1 / tier2 / tier3

    classification: str = "unknown"
    classification_confidence: float = 0.0
    current_owner: str = "incident_lead_agent"
    hop_count: int = 0

    actions_attempted: List[ActionAttempt] = field(default_factory=list)
    articles_shown: List[ArticleMatch] = field(default_factory=list)

    room_agents: List[str] = field(default_factory=list)
    room_members: List[str] = field(default_factory=list)
    diagnostics_collected: List[str] = field(default_factory=list)

    hypothesis: Optional[str] = None
    resolution: Optional[str] = None
    escalation_reason: Optional[str] = None
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def log_action(self, agent: str, action: str, tier: int, outcome: str, detail: str = None):
        self.actions_attempted.append(
            ActionAttempt(agent=agent, action=action, tier=tier, outcome=outcome, detail=detail)
        )

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_incident(cls, incident) -> "IncidentState":
        """Build a fresh state from an Incident ORM object."""
        return cls(
            incident_id=incident.incident_id,
            incident_number=incident.incident_number,
            platform=incident.platform or "unix",
            ci_criticality=incident.ci_criticality or "tier2",
        )
