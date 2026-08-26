from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.exceptions import GoogleCalendarError
from app.dependencies.auth_dependencies import require_active_business
from app.dependencies.db_dependencies import get_db
from app.models.business import Business
from app.schemas.common import Envelope, ResponseMeta
from app.schemas.google_calendar import GoogleCalendarConnectUrlOut, GoogleCalendarStatusOut, UpcomingEventOut
from app.services.google_calendar_service import GoogleCalendarService

router = APIRouter(prefix="/google-calendar", tags=["google-calendar"])


def _envelope(data):
    return Envelope(data=data, meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))


@router.get("/connect", response_model=Envelope[GoogleCalendarConnectUrlOut])
def connect(business: Business = Depends(require_active_business), db: Session = Depends(get_db)):
    url = GoogleCalendarService(db).get_authorize_url(business.id)
    return _envelope(GoogleCalendarConnectUrlOut(url=url))


@router.get("/oauth/callback")
async def oauth_callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
    db: Session = Depends(get_db),
):
    """
    Hit directly by the founder's browser via Google's own redirect, not
    by the frontend's fetch logic - so this always returns a real HTTP
    redirect back into the app, success or failure, never a JSON error
    response the browser would just render as a blank page.
    """
    service = GoogleCalendarService(db)

    if error:
        return RedirectResponse(
            service.build_redirect_url(success=False, message=error_description or error)
        )
    if not code or not state:
        return RedirectResponse(
            service.build_redirect_url(success=False, message="Missing authorization code from Google.")
        )

    try:
        await service.complete_oauth(code=code, state=state)
    except GoogleCalendarError as exc:
        return RedirectResponse(service.build_redirect_url(success=False, message=exc.message))

    return RedirectResponse(service.build_redirect_url(success=True))


@router.get("/status", response_model=Envelope[GoogleCalendarStatusOut])
def status(business: Business = Depends(require_active_business), db: Session = Depends(get_db)):
    return _envelope(GoogleCalendarStatusOut(**GoogleCalendarService(db).get_status(business.id)))


@router.delete("/disconnect")
def disconnect(business: Business = Depends(require_active_business), db: Session = Depends(get_db)):
    GoogleCalendarService(db).disconnect(business.id)
    return _envelope({"disconnected": True})


@router.get("/upcoming-events", response_model=Envelope[list[UpcomingEventOut]])
async def upcoming_events(business: Business = Depends(require_active_business), db: Session = Depends(get_db)):
    events = await GoogleCalendarService(db).get_upcoming_events(business.id)
    return _envelope([UpcomingEventOut(**e) for e in events])
