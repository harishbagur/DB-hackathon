"""
Guardrails — action tier enforcement before any execution.

Tier 0: Read-only diagnostics         — always allowed
Tier 1: Low-risk, reversible actions  — auto-execute, notify after
Tier 2: Config changes / critical CIs — human must approve in chat
Tier 3: Data / security / Tier-0 CIs  — agents advise only, never act
"""
from dataclasses import dataclass
from app.core.state import IncidentState


# CI criticality → minimum tier required to auto-execute
_CI_TIER_FLOOR = {
    "tier0": 3,   # Tier-0 CI: nothing auto-executes, human only
    "tier1": 2,   # Tier-1 CI: Tier 2 approval needed for any action
    "tier2": 1,   # Tier-2 CI: Tier 1 actions auto-execute
    "tier3": 1,   # Tier-3 CI: Tier 1 actions auto-execute
}


@dataclass
class GuardrailResult:
    allowed: bool
    effective_tier: int          # may be promoted above the requested tier
    reason: str


def check(state: IncidentState, requested_tier: int) -> GuardrailResult:
    """
    Decide whether an action of `requested_tier` is allowed to auto-execute
    given the incident's CI criticality.

    Returns GuardrailResult with allowed=True/False and effective_tier.
    """
    ci_floor = _CI_TIER_FLOOR.get(state.ci_criticality, 1)

    # Promote tier if CI criticality demands it
    effective_tier = max(requested_tier, ci_floor)

    if effective_tier >= 2:
        return GuardrailResult(
            allowed=False,
            effective_tier=effective_tier,
            reason=(
                f"Action requires Tier {effective_tier} approval. "
                f"CI criticality is {state.ci_criticality}. "
                f"A human must approve in the chat room before this executes."
            ),
        )

    return GuardrailResult(
        allowed=True,
        effective_tier=effective_tier,
        reason="Auto-execute permitted (Tier 1, reversible).",
    )
