"""
BaseAgent — shared setup for all agents.

If ANTHROPIC_API_KEY is set   → calls Claude for real.
If ANTHROPIC_API_KEY is empty → returns mock_response() so the demo
                                 runs without a key.
"""
import json
from app.config import settings


class BaseAgent:
    MODEL = "claude-sonnet-4-6"

    def __init__(self):
        self._client = None
        if settings.ANTHROPIC_API_KEY:
            import anthropic
            self._client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    def call_claude(self, system: str, user: str) -> dict:
        """
        Call Claude and parse the JSON response.
        Falls back to mock_response() if no API key is configured.
        """
        if self._client is None:
            return self.mock_response()

        response = self._client.messages.create(
            model=self.MODEL,
            max_tokens=1000,
            system=system + "\n\nAlways respond with valid JSON only. No extra text.",
            messages=[{"role": "user", "content": user}],
        )
        raw = response.content[0].text.strip()
        # Strip markdown code fences if Claude adds them
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)

    def mock_response(self) -> dict:
        """
        Override in each subclass to return a plausible mock.
        Used when ANTHROPIC_API_KEY is not set.
        """
        raise NotImplementedError
