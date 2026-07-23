from pydantic import BaseModel
from typing import Optional


class AgentResponse(BaseModel):
    agent_id: int
    agent_name: str
    agent_type: str
    status: str
    confidence_score: Optional[float]

    class Config:
        from_attributes = True


class AddAgentRequest(BaseModel):
    agent_id: int     # unix agent = 4, windows agent = 5 (from seed data)
