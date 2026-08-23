from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.dependencies.auth_dependencies import get_current_user, require_active_business
from app.dependencies.db_dependencies import get_db
from app.models.business import Business
from app.models.user import User
from app.repositories.business_repository import BusinessRepository
from app.schemas.analytics import BusinessAnalyticsOut
from app.schemas.common import Envelope, ResponseMeta
from app.services.analytics_service import AnalyticsService
from app.services.demo_data_service import DemoDataService
from app.services.export_service import ExportService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/business", response_model=Envelope[BusinessAnalyticsOut])
def business_analytics(
    days: int = Query(default=90, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.onboarding_completed:
        return Envelope(
            data=DemoDataService.business_analytics(days),
            meta=ResponseMeta(generated_at=datetime.now(timezone.utc)),
        )

    business: Business | None = BusinessRepository(db).get_active_for_user(current_user.id)
    if not business:
        raise NotFoundError("No active business found. Complete onboarding to create one.")
    data = AnalyticsService(db).get_business_analytics(business.id, days)
    return Envelope(data=data, meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))


def _csv_response(content: str, filename: str) -> Response:
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/tasks")
def export_tasks_csv(business: Business = Depends(require_active_business), db: Session = Depends(get_db)):
    csv_content = ExportService(db).tasks_csv(business.id)
    return _csv_response(csv_content, "tasks.csv")


@router.get("/export/revenue")
def export_revenue_csv(business: Business = Depends(require_active_business), db: Session = Depends(get_db)):
    csv_content = ExportService(db).revenue_csv(business.id)
    return _csv_response(csv_content, "revenue.csv")