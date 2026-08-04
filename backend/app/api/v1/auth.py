from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.dependencies.auth_dependencies import get_current_user
from app.dependencies.db_dependencies import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, SignupRequest, UserOut
from app.schemas.common import Envelope, ResponseMeta
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

# Locally, frontend (localhost:3000) and backend (localhost:8000) share the
# same "site" (site is judged by domain, ignoring port), so Lax works fine.
# In production, frontend (Vercel) and backend (Railway) are genuinely
# different domains - a cross-site fetch - which Lax cookies are blocked on.
# SameSite=None allows that, but browsers require Secure=True alongside it,
# which is already the case since both are served over HTTPS in production.
_is_production = settings.ENVIRONMENT == "production"
COOKIE_KWARGS = dict(
    httponly=True,
    secure=True,
    samesite="none" if _is_production else "lax",
)


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie("access_token", access_token, max_age=15 * 60, **COOKIE_KWARGS)
    response.set_cookie("refresh_token", refresh_token, max_age=7 * 24 * 60 * 60, **COOKIE_KWARGS)


@router.post("/signup", response_model=Envelope[UserOut])
def signup(payload: SignupRequest, response: Response, db: Session = Depends(get_db)):
    service = AuthService(db)
    user, access_token, refresh_token = service.signup(payload.email, payload.password, payload.name)
    _set_auth_cookies(response, access_token, refresh_token)
    return Envelope(data=UserOut.model_validate(user), meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))


@router.post("/login", response_model=Envelope[UserOut])
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    service = AuthService(db)
    user, access_token, refresh_token = service.login(payload.email, payload.password)
    _set_auth_cookies(response, access_token, refresh_token)
    return Envelope(data=UserOut.model_validate(user), meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return Envelope(data={"logged_out": True}, meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))


@router.get("/me", response_model=Envelope[UserOut])
def me(current_user: User = Depends(get_current_user)):
    return Envelope(
        data=UserOut.model_validate(current_user),
        meta=ResponseMeta(generated_at=datetime.now(timezone.utc)),
    )
