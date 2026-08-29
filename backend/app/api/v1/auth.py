from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.dependencies.auth_dependencies import get_current_user
from app.dependencies.db_dependencies import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    ResetPasswordRequest,
    SignupRequest,
    UpdateUserPreferencesRequest,
    UserOut,
)
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
    secure=_is_production,
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


@router.patch("/me", response_model=Envelope[UserOut])
def update_me(
    payload: UpdateUserPreferencesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    current_user = UserRepository(db).save(current_user)
    return Envelope(
        data=UserOut.model_validate(current_user),
        meta=ResponseMeta(generated_at=datetime.now(timezone.utc)),
    )


_GENERIC_RESET_MESSAGE = "If an account with that email exists, we've sent password reset instructions."


@router.post("/forgot-password", response_model=Envelope[ForgotPasswordResponse])
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    raw_token = service.request_password_reset(payload.email)

    data = ForgotPasswordResponse(message=_GENERIC_RESET_MESSAGE)
    if raw_token and settings.ENVIRONMENT != "production":
        # AuthService.request_password_reset also sends a real email via
        # Resend (see email_service.py) - this dev-mode raw-token-in-
        # response path is additional, not a replacement, so local
        # dev/testing still works without depending on inbox access.
        data.reset_token = raw_token
        data.reset_url = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"

    return Envelope(data=data, meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    AuthService(db).reset_password(payload.token, payload.new_password)
    return Envelope(data={"reset": True}, meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))
