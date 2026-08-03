"""
Aggregates every v1 sub-router into one APIRouter that main.py mounts
under settings.API_V1_PREFIX. Adding a new module later is one import
and one include_router line here.
"""
from fastapi import APIRouter

from app.api.v1 import (
    assistant,
    auth,
    business_builder,
    businesses,
    ceo_briefing,
    goals,
    health_score,
    onboarding,
    projects,
    revenue,
    tasks,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(onboarding.router)
api_router.include_router(businesses.router)
api_router.include_router(goals.router)
api_router.include_router(projects.router)
api_router.include_router(tasks.router)
api_router.include_router(revenue.router)
api_router.include_router(health_score.router)
api_router.include_router(business_builder.router)
api_router.include_router(ceo_briefing.router)
api_router.include_router(assistant.router)
