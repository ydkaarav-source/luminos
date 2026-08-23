"""
Rate limiting for this app's AI-calling endpoints (real OpenAI cost
per request): POST /business-builder/generate, POST /assistant/message,
POST /health-score/recalculate, GET /ceo-briefing/today.

Production runs a single uvicorn worker (see backend/Dockerfile's CMD -
no --workers flag, no Railway config overriding it), so an in-memory
limiter is correct here: state living in one process is exactly what's
needed, and adding Redis or any other shared store would be
infrastructure this app doesn't need yet. If a second worker is ever
added, this in-memory store would need to move to a shared backend
(slowapi supports Redis via `storage_uri` with no other code changes),
since each worker would otherwise keep its own separate counters.

Scoped per authenticated user, not IP - every route this protects
already requires auth via its own dependencies, so the user id is the
accurate unit of abuse; IP would over- or under-count for shared
networks and NATs.
"""
from uuid import UUID

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.security import decode_token
from app.db.session import SessionLocal
from app.models.user import User


def _user_key(request: Request) -> str:
    token = request.cookies.get("access_token")
    if token:
        payload = decode_token(token)
        if payload and payload.get("type") == "access":
            return f"user:{payload['sub']}"
    # No valid session - every route this decorates also requires auth
    # via its own dependencies, so this shouldn't be reachable in
    # practice. Fall back to IP so the limiter itself never errors.
    return get_remote_address(request)


def is_demo_request(request: Request) -> bool:
    """
    True if this request will be served by Demo Mode's fictional data
    path (an un-onboarded user) rather than a real OpenAI call - used
    as `exempt_when` on /ceo-briefing/today so demo traffic, which
    never touches OpenAI, never counts against the limit.
    """
    token = request.cookies.get("access_token")
    if not token:
        return False
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return False

    db = SessionLocal()
    try:
        user = db.get(User, UUID(payload["sub"]))
        return bool(user and not user.onboarding_completed)
    finally:
        db.close()


limiter = Limiter(key_func=_user_key)
