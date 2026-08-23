from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.exceptions import StripeConnectError
from app.dependencies.auth_dependencies import require_active_business
from app.dependencies.db_dependencies import get_db
from app.models.business import Business
from app.schemas.common import Envelope, ResponseMeta
from app.schemas.stripe import StripeConnectUrlOut, StripeStatusOut, StripeSyncResultOut
from app.services.stripe_service import StripeService

router = APIRouter(prefix="/stripe", tags=["stripe"])


def _envelope(data):
    return Envelope(data=data, meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))


@router.get("/connect", response_model=Envelope[StripeConnectUrlOut])
def connect(business: Business = Depends(require_active_business), db: Session = Depends(get_db)):
    url = StripeService(db).get_authorize_url(business.id)
    return _envelope(StripeConnectUrlOut(url=url))


@router.get("/oauth/callback")
async def oauth_callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
    db: Session = Depends(get_db),
):
    """
    Hit directly by the founder's browser via Stripe's own redirect, not
    by the frontend's fetch logic - so this always returns a real HTTP
    redirect back into the app, success or failure, never a JSON error
    response the browser would just render as a blank page.
    """
    service = StripeService(db)

    if error:
        return RedirectResponse(
            service.build_redirect_url(success=False, message=error_description or error)
        )
    if not code or not state:
        return RedirectResponse(
            service.build_redirect_url(success=False, message="Missing authorization code from Stripe.")
        )

    try:
        await service.complete_oauth(code=code, state=state)
    except StripeConnectError as exc:
        return RedirectResponse(service.build_redirect_url(success=False, message=exc.message))

    return RedirectResponse(service.build_redirect_url(success=True))


@router.get("/status", response_model=Envelope[StripeStatusOut])
def status(business: Business = Depends(require_active_business), db: Session = Depends(get_db)):
    return _envelope(StripeStatusOut(**StripeService(db).get_status(business.id)))


@router.post("/sync", response_model=Envelope[StripeSyncResultOut])
async def sync(business: Business = Depends(require_active_business), db: Session = Depends(get_db)):
    result = await StripeService(db).sync_transactions(business.id)
    return _envelope(StripeSyncResultOut(**result))
