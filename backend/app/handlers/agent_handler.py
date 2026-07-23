from typing import List
from sqlalchemy.orm import Session

from app.models.agent import AIAgent
from app.schemas.agent import AgentResponse


def list_agents(db: Session) -> List[AgentResponse]:
    agents = db.query(AIAgent).all()
    return [AgentResponse.model_validate(a) for a in agents]
