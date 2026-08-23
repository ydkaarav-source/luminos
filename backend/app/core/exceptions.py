"""
Custom exception hierarchy + FastAPI exception handlers.

Every error the API returns follows the same envelope:
    { "error": { "code": "...", "message": "...", "details": {} } }
"""
import time

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded


class LuminOSError(Exception):
    code = "INTERNAL_ERROR"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str, details: dict | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class NotFoundError(LuminOSError):
    code = "NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND


class UnauthorizedError(LuminOSError):
    code = "UNAUTHORIZED"
    status_code = status.HTTP_401_UNAUTHORIZED


class ForbiddenError(LuminOSError):
    code = "FORBIDDEN"
    status_code = status.HTTP_403_FORBIDDEN


class ConflictError(LuminOSError):
    code = "CONFLICT"
    status_code = status.HTTP_409_CONFLICT


class AIProviderError(LuminOSError):
    code = "AI_PROVIDER_ERROR"
    status_code = status.HTTP_502_BAD_GATEWAY


class WebsiteUnreachableError(LuminOSError):
    code = "WEBSITE_UNREACHABLE"
    status_code = status.HTTP_502_BAD_GATEWAY


class StripeConnectError(LuminOSError):
    code = "STRIPE_CONNECT_ERROR"
    status_code = status.HTTP_502_BAD_GATEWAY


def _envelope(code: str, message: str, details: dict | None = None) -> dict:
    return {"error": {"code": code, "message": message, "details": details or {}}}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(LuminOSError)
    async def handle_luminos_error(request: Request, exc: LuminOSError):
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RateLimitExceeded)
    async def handle_rate_limit_exceeded(request: Request, exc: RateLimitExceeded):
        reset_message = "shortly"
        view_limit = getattr(request.state, "view_rate_limit", None)
        if view_limit:
            try:
                reset_at, _ = request.app.state.limiter.limiter.get_window_stats(*view_limit)
                minutes = max(int(reset_at - time.time()) // 60, 1)
                reset_message = f"in about {minutes} minute{'s' if minutes != 1 else ''}"
            except Exception:  # noqa: BLE001 - never let a header/stats lookup break the error response
                pass
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=_envelope(
                "RATE_LIMIT_EXCEEDED",
                f"You're sending requests too quickly ({exc.detail}). Try again {reset_message}.",
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_envelope(
                "VALIDATION_ERROR", "One or more fields are invalid.", {"errors": exc.errors()}
            ),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_envelope("INTERNAL_ERROR", "Something went wrong. Please try again."),
        )
