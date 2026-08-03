from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.auth_dependencies import get_current_user, require_active_business
from app.dependencies.db_dependencies import get_db
from app.models.business import Business
from app.models.user import User
from app.repositories.business_repository import BusinessRepository
from app.schemas.business import BusinessOut, BusinessUpdateRequest
from app.schemas.common import Envelope, ResponseMeta

router = APIRouter(prefix="/businesses", tags=["businesses"])


def _envelope(data):
    return Envelope(data=data, meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))


@router.get("", response_model=Envelope[list[BusinessOut]])
def list_businesses(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    businesses = BusinessRepository(db).list_for_user(current_user.id)
    return _envelope([BusinessOut.model_validate(b) for b in businesses])


@router.get("/active", response_model=Envelope[BusinessOut])
def get_active(business: Business = Depends(require_active_business)):
    return _envelope(BusinessOut.model_validate(business))


@router.patch("/active", response_model=Envelope[BusinessOut])
def update_active(
    payload: BusinessUpdateRequest,
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(business, field, value)
    business = BusinessRepository(db).save(business)
    return _envelope(BusinessOut.model_validate(business))
