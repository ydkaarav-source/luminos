from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies.auth_dependencies import require_active_business
from app.dependencies.db_dependencies import get_db
from app.models.business import Business
from app.schemas.analytics import BusinessAnalyticsOut
from app.schemas.common import Envelope, ResponseMeta
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/business", response_model=Envelope[BusinessAnalyticsOut])
def business_analytics(
    days: int = Query(default=90, ge=7, le=365),
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    data = AnalyticsService(db).get_business_analytics(business.id, days)
    return Envelope(data=data, meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))