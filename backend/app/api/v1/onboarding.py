from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.auth_dependencies import get_current_user
from app.dependencies.db_dependencies import get_db
from app.models.user import User
from app.repositories.business_repository import BusinessRepository
from app.schemas.business import BusinessOut
from app.schemas.common import Envelope, ResponseMeta
from app.schemas.onboarding import (
    BusinessStepRequest,
    OnboardingStatusOut,
    ProfileStepRequest,
    ResourcesStepRequest,
)
from app.services.onboarding_service import OnboardingService

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


def _envelope(data):
    return Envelope(data=data, meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))


@router.get("/status", response_model=Envelope[OnboardingStatusOut])
def status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    has_business = bool(BusinessRepository(db).get_active_for_user(current_user.id))
    return _envelope(
        OnboardingStatusOut(
            onboarding_completed=current_user.onboarding_completed, has_business=has_business
        )
    )


@router.post("/profile")
def profile_step(
    payload: ProfileStepRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    OnboardingService(db).save_profile_step(current_user, payload)
    return _envelope({"saved": True})


@router.post("/business", response_model=Envelope[BusinessOut])
def business_step(
    payload: BusinessStepRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    business = OnboardingService(db).save_business_step(current_user, payload)
    return _envelope(BusinessOut.model_validate(business))


@router.post("/resources", response_model=Envelope[BusinessOut])
def resources_step(
    payload: ResourcesStepRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    business = BusinessRepository(db).get_active_for_user(current_user.id)
    business = OnboardingService(db).save_resources_step(business, payload)
    return _envelope(BusinessOut.model_validate(business))


@router.post("/complete")
def complete(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    OnboardingService(db).complete(current_user)
    return _envelope({"onboarding_completed": True})
