from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.dependencies.auth_dependencies import get_current_user, require_active_business
from app.dependencies.db_dependencies import get_db
from app.models.ai_insight import AIInsight
from app.models.business import Business
from app.models.user import User
from app.schemas.ai import CEOBriefingOut
from app.schemas.common import Envelope, ResponseMeta
from app.services.ceo_briefing_service import CEOBriefingService

router = APIRouter(prefix="/ceo-briefing", tags=["ceo-briefing"])


def _envelope(data):
    return Envelope(data=data, meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))


@router.get("/today", response_model=Envelope[CEOBriefingOut])
async def today(
    business: Business = Depends(require_active_business),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CEOBriefingService(db)
    briefing = await service.generate_today(business, current_user.id)
    return _envelope(CEOBriefingOut.model_validate(briefing))


@router.get("/history", response_model=Envelope[list[CEOBriefingOut]])
def history(business: Business = Depends(require_active_business), db: Session = Depends(get_db)):
    briefings = CEOBriefingService(db).get_history(business.id)
    return _envelope([CEOBriefingOut.model_validate(b) for b in briefings])


@router.post("/{insight_id}/mark-read", response_model=Envelope[CEOBriefingOut])
def mark_read(
    insight_id: UUID,
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    insight = db.get(AIInsight, insight_id)
    if not insight or insight.business_id != business.id:
        raise NotFoundError("Briefing not found.")
    insight = CEOBriefingService(db).mark_read(insight)
    return _envelope(CEOBriefingOut.model_validate(insight))
