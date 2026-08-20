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
from app.repositories.business_repository import BusinessRepository
from app.schemas.ai import CEOBriefingOut
from app.schemas.common import Envelope, ResponseMeta
from app.services.ceo_briefing_service import CEOBriefingService
from app.services.demo_data_service import DemoDataService

router = APIRouter(prefix="/ceo-briefing", tags=["ceo-briefing"])


def _envelope(data):
    return Envelope(data=data, meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))


@router.get("/today", response_model=Envelope[CEOBriefingOut])
async def today(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.onboarding_completed:
        return _envelope(DemoDataService.ceo_briefing())

    business = BusinessRepository(db).get_active_for_user(current_user.id)
    if not business:
        raise NotFoundError("No active business found. Complete onboarding to create one.")
    service = CEOBriefingService(db)
    briefing = await service.generate_today(business, current_user.id)
    return _envelope(CEOBriefingOut.from_insight(briefing))


@router.get("/history", response_model=Envelope[list[CEOBriefingOut]])
def history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # No demo history is generated (Demo Mode only defines a single
    # "today" briefing) - an un-onboarded user simply has no previous
    # briefings, same as a real new business would. This also keeps the
    # /ceo-briefing page's Promise.all([today, history]) from rejecting
    # as a whole when there's no business yet, which would otherwise
    # swallow the demo "today" briefing along with it.
    if not current_user.onboarding_completed:
        return _envelope([])

    business = BusinessRepository(db).get_active_for_user(current_user.id)
    if not business:
        raise NotFoundError("No active business found. Complete onboarding to create one.")
    briefings = CEOBriefingService(db).get_history(business.id)
    return _envelope([CEOBriefingOut.from_insight(b) for b in briefings])


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
    return _envelope(CEOBriefingOut.from_insight(insight))
