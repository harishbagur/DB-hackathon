from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.metrics import ExecutiveMetrics
from app.models.compliance import DoraCompliance
from app.schemas.dashboard import ExecutiveMetricsResponse, DoraResponse


def get_executive_metrics(db: Session) -> ExecutiveMetricsResponse:
    metrics = (
        db.query(ExecutiveMetrics)
        .order_by(ExecutiveMetrics.metric_date.desc())
        .first()
    )
    if not metrics:
        raise HTTPException(status_code=404, detail="No metrics available")
    return ExecutiveMetricsResponse.model_validate(metrics)


def get_dora_compliance(db: Session) -> DoraResponse:
    compliance = db.query(DoraCompliance).first()
    if not compliance:
        raise HTTPException(status_code=404, detail="No DORA compliance data available")
    return DoraResponse.model_validate(compliance)
