from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.dependencies.auth_dependencies import get_current_user, require_active_business
from app.dependencies.db_dependencies import get_db
from app.models.business import Business
from app.models.user import User
from app.schemas.common import Envelope, ResponseMeta
from app.schemas.website_brief import (
    WebsiteBriefGenerateRequest,
    WebsiteBriefOut,
    WebsiteScrapeRequest,
    WebsiteScrapeResponse,
)
from app.services.website_brief_service import WebsiteBriefService

router = APIRouter(prefix="/website-brief", tags=["website-brief"])


def _envelope(data):
    return Envelope(data=data, meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))


@router.post("/generate", response_model=Envelope[WebsiteBriefOut])
async def generate(
    payload: WebsiteBriefGenerateRequest,
    business: Business = Depends(require_active_business),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = WebsiteBriefService(db)
    brief = await service.generate_brief(business, current_user.id)
    return _envelope(WebsiteBriefOut.model_validate(brief))


@router.get("/latest", response_model=Envelope[WebsiteBriefOut])
def latest(business: Business = Depends(require_active_business), db: Session = Depends(get_db)):
    brief = WebsiteBriefService(db).get_latest(business.id)
    if not brief:
        raise NotFoundError("No website brief generated yet.")
    return _envelope(WebsiteBriefOut.model_validate(brief))


@router.post("/scrape-site", response_model=Envelope[WebsiteScrapeResponse])
async def scrape_site(
    payload: WebsiteScrapeRequest,
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    brief, content = await WebsiteBriefService(db).scrape_site(business, str(payload.url))
    preview = content[:300] + "…" if len(content) > 300 else content
    return _envelope(
        WebsiteScrapeResponse(brief=WebsiteBriefOut.model_validate(brief), content_preview=preview)
    )
