from fastapi import APIRouter

from app.api.v1 import (
    analytics,
    assistant,
    auth,
    business_builder,
    business_profile,
    businesses,
    ceo_briefing,
    goals,
    health_score,
    memory,
    onboarding,
    projects,
    revenue,
    tasks,
    trades,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(onboarding.router)
api_router.include_router(businesses.router)
api_router.include_router(business_profile.router)
api_router.include_router(goals.router)
api_router.include_router(projects.router)
api_router.include_router(tasks.router)
api_router.include_router(revenue.router)
api_router.include_router(health_score.router)
api_router.include_router(business_builder.router)
api_router.include_router(ceo_briefing.router)
api_router.include_router(assistant.router)
api_router.include_router(trades.router)
api_router.include_router(analytics.router)
api_router.include_router(memory.router)