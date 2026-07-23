from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.handlers import dashboard_handler
from app.schemas.dashboard import ExecutiveMetricsResponse, DoraResponse

router = APIRouter()


@router.get("/executive", response_model=ExecutiveMetricsResponse)
def executive_metrics(db: Session = Depends(get_db)):
    """Executive dashboard — resolution rates, MTTR, critical incidents, scores."""
    return dashboard_handler.get_executive_metrics(db)


@router.get("/dora", response_model=DoraResponse)
def dora_compliance(db: Session = Depends(get_db)):
    """DORA compliance breakdown across all five pillars."""
    return dashboard_handler.get_dora_compliance(db)
