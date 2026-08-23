from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.core.rate_limit import limiter
from app.dependencies.auth_dependencies import get_current_user, require_active_business
from app.dependencies.db_dependencies import get_db
from app.models.business import Business
from app.models.user import User
from app.schemas.business_plan import BusinessBuilderGenerateRequest, BusinessPlanOut
from app.schemas.common import Envelope, ResponseMeta
from app.services.business_builder_service import BusinessBuilderService

router = APIRouter(prefix="/business-builder", tags=["business-builder"])


def _envelope(data):
    return Envelope(data=data, meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))


@router.post("/generate", response_model=Envelope[BusinessPlanOut])
@limiter.limit("5/hour")
async def generate(
    request: Request,
    payload: BusinessBuilderGenerateRequest,
    business: Business = Depends(require_active_business),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = BusinessBuilderService(db)
    plan = await service.generate_plan(business, payload.idea_description, current_user.id)
    return _envelope(BusinessPlanOut.model_validate(plan))


@router.get("/plans", response_model=Envelope[list[BusinessPlanOut]])
def list_plans(business: Business = Depends(require_active_business), db: Session = Depends(get_db)):
    plans = BusinessBuilderService(db).list_plans(business.id)
    return _envelope([BusinessPlanOut.model_validate(p) for p in plans])


@router.get("/plans/{plan_id}", response_model=Envelope[BusinessPlanOut])
def get_plan(
    plan_id: UUID,
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    plan = BusinessBuilderService(db).get_plan(plan_id)
    if not plan or plan.business_id != business.id:
        raise NotFoundError("Business plan not found.")
    return _envelope(BusinessPlanOut.model_validate(plan))
