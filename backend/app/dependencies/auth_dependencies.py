"""
Auth dependencies: resolve the current user from the access-token
cookie, and resolve the user's active business for business-scoped
routes so handlers never re-fetch it manually.
"""
from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, UnauthorizedError
from app.core.security import decode_token
from app.dependencies.db_dependencies import get_db
from app.models.business import Business
from app.models.user import User


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise UnauthorizedError("You need to be logged in to do that.")

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise UnauthorizedError("Your session has expired. Please log in again.")

    user = db.get(User, UUID(payload["sub"]))
    if not user:
        raise UnauthorizedError("Your session has expired. Please log in again.")

    return user


def require_active_business(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Business:
    """
    Resolves the user's active business so every business-scoped route
    gets it injected rather than re-querying it in every handler.
    """
    business = (
        db.query(Business)
        .filter(Business.user_id == current_user.id, Business.is_active.is_(True))
        .order_by(Business.created_at.desc())
        .first()
    )
    if not business:
        raise NotFoundError(
            "No active business found. Complete onboarding to create one."
        )
    return business
