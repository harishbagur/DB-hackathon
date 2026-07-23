from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.handlers import agent_handler
from app.schemas.agent import AgentResponse

router = APIRouter()


@router.get("/", response_model=List[AgentResponse])
def list_agents(db: Session = Depends(get_db)):
    """List all AI agents and their current status."""
    return agent_handler.list_agents(db)
