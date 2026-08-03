"""
Application factory. Registers middleware, exception handlers, and the
versioned API router. Run with:

    uvicorn app.main:app --reload
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.db import model_registry  # noqa: F401 - populates Base.metadata at startup
from app.middleware.request_logging import RequestLoggingMiddleware
configure_logging()

app = FastAPI(
    title=settings.APP_NAME,
    description="The AI operating system for entrepreneurs.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

register_exception_handlers(app)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["system"])
def health_check():
    """Liveness probe for Docker/orchestrators - no DB round trip."""
    return {"status": "ok", "service": settings.APP_NAME}
