from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.dependencies.auth_dependencies import get_current_user, require_active_business
from app.dependencies.db_dependencies import get_db
from app.models.business import Business
from app.models.user import User
from app.repositories.business_repository import BusinessRepository
from app.schemas.common import Envelope, ResponseMeta
from app.schemas.health_score import HealthScoreOut
from app.services.demo_data_service import DemoDataService
from app.services.health_score_service import HealthScoreService

router = APIRouter(prefix="/health-score", tags=["health-score"])


def _envelope(data):
    return Envelope(data=data, meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))


@router.get("/latest", response_model=Envelope[HealthScoreOut | None])
def latest(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.onboarding_completed:
        return _envelope(DemoDataService.health_score())

    business = BusinessRepository(db).get_active_for_user(current_user.id)
    if not business:
        raise NotFoundError("No active business found. Complete onboarding to create one.")
    score = HealthScoreService(db).get_latest(business.id)
    return _envelope(HealthScoreOut.model_validate(score) if score else None)


@router.get("/history", response_model=Envelope[list[HealthScoreOut]])
def history(business: Business = Depends(require_active_business), db: Session = Depends(get_db)):
    scores = HealthScoreService(db).get_history(business.id)
    return _envelope([HealthScoreOut.model_validate(s) for s in scores])


@router.post("/recalculate", response_model=Envelope[HealthScoreOut])
async def recalculate(
    business: Business = Depends(require_active_business),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    score = await HealthScoreService(db).recalculate(business, current_user.id)
    return _envelope(HealthScoreOut.model_validate(score))
