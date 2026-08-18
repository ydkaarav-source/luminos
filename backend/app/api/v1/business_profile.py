from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.dependencies.auth_dependencies import require_active_business
from app.dependencies.db_dependencies import get_db
from app.models.business import Business
from app.repositories.business_profile_repository import BusinessProfileRepository
from app.schemas.business_profile import BusinessProfileCreateRequest, BusinessProfileOut
from app.schemas.common import Envelope, ResponseMeta

router = APIRouter(prefix="/business-profile", tags=["business-profile"])


def _envelope(data):
    return Envelope(data=data, meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))


@router.get("", response_model=Envelope[BusinessProfileOut])
def get_profile(
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    profile = BusinessProfileRepository(db).get_by_business_id(business.id)
    if not profile:
        raise NotFoundError(
            "No business profile found yet - complete onboarding or fill this in from settings."
        )
    return _envelope(BusinessProfileOut.model_validate(profile))


@router.put("", response_model=Envelope[BusinessProfileOut])
def update_profile(
    payload: BusinessProfileCreateRequest,
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    profile = BusinessProfileRepository(db).upsert(business.id, payload.model_dump(exclude_unset=True))
    return _envelope(BusinessProfileOut.model_validate(profile))
