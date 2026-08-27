from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.auth_dependencies import require_active_business
from app.dependencies.db_dependencies import get_db
from app.models.business import Business
from app.schemas.common import Envelope, ResponseMeta
from app.schemas.opportunity import OpportunityFindingOut
from app.services.opportunity_radar_service import OpportunityRadarService

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


def _envelope(data):
    return Envelope(data=data, meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))


@router.get("", response_model=Envelope[list[OpportunityFindingOut]])
def list_findings(business: Business = Depends(require_active_business), db: Session = Depends(get_db)):
    findings = OpportunityRadarService(db).get_active(business.id)
    return _envelope([OpportunityFindingOut.model_validate(f) for f in findings])


@router.post("/{finding_id}/dismiss", response_model=Envelope[OpportunityFindingOut])
def dismiss(
    finding_id: UUID,
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    finding = OpportunityRadarService(db).dismiss(finding_id, business.id)
    return _envelope(OpportunityFindingOut.model_validate(finding))
