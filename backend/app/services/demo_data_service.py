"""
Demo Mode data generator.

Users who haven't completed onboarding yet have no real Business, tasks,
or revenue to show - Dashboard, Health Score, and Analytics would just be
empty. This module returns a realistic FICTIONAL business ("Northstar
Coffee Co.", a coffee subscription business) shaped exactly like the real
HealthScoreOut / CEOBriefingOut / BusinessAnalyticsOut schemas, so those
pages have something to show before a user has logged anything real.

Nothing here is ever persisted: every method is a pure function that
builds and returns a schema instance directly - there is no db session,
no ORM model, and no db.add/db.commit anywhere in this file. Callers are
responsible for setting is_demo=True on the response so the frontend can
render its "Demo" label; this service always does so on the objects it
returns.

The story is deterministic (fixed random seed, fixed IDs) so every
un-onboarded user sees the same numbers rather than a fresh random set on
every page load - this reads as one consistent example, not noise.
"""
import random
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.schemas.ai import CEOBriefingOut
from app.schemas.analytics import BusinessAnalyticsOut, HealthScorePoint, RevenuePoint, TaskCompletionPoint
from app.schemas.health_score import HealthScoreOut

_DEMO_SEED = 20240601
_DEMO_HEALTH_SCORE_ID = UUID("de000000-0000-0000-0000-000000000001")
_DEMO_BRIEFING_ID = UUID("de000000-0000-0000-0000-000000000002")

_DEMO_ANALYTICS_WINDOW_DAYS = 28


class DemoDataService:
    """Builds fictional Northstar Coffee Co. data for Demo Mode."""

    BUSINESS_NAME = "Northstar Coffee Co."

    @staticmethod
    def health_score() -> HealthScoreOut:
        sub_scores = {
            "revenue_score": 82,
            "operations_score": 68,
            "marketing_score": 71,
            "customer_growth_score": 65,
            "financial_management_score": 79,
        }
        overall_score = round(sum(sub_scores.values()) / len(sub_scores))

        ai_explanation = {
            "cfo": {
                "strengths": ["Subscription revenue has grown for three consecutive weeks."],
                "weaknesses": ["Customer acquisition cost isn't tracked yet."],
                "recommendations": ["Set a monthly recurring revenue target and track churn explicitly."],
            },
            "cmo": {
                "strengths": ["Instagram engagement is trending up alongside new subscriber signups."],
                "weaknesses": ["No referral or loyalty program exists yet."],
                "recommendations": ["Launch a simple referral incentive for existing subscribers."],
            },
            "coo": {
                "strengths": ["Task completion rate has held steady week over week."],
                "weaknesses": ["Fulfillment tasks occasionally slip past their due date."],
                "recommendations": ["Batch weekly fulfillment tasks earlier in the week to build in a buffer."],
            },
            "cro": {
                "strengths": ["New subscriber signups are outpacing cancellations."],
                "weaknesses": ["No win-back flow exists for lapsed subscribers."],
                "recommendations": ["Set up a simple win-back email for canceled subscriptions."],
            },
            "ceo": {
                "strengths": ["Revenue and subscriber growth are both trending in the right direction."],
                "weaknesses": ["Operational tracking hasn't caught up with growth yet."],
                "recommendations": [
                    "Keep growth steady while building out the operational tracking that's currently missing."
                ],
            },
        }

        return HealthScoreOut(
            id=_DEMO_HEALTH_SCORE_ID,
            overall_score=overall_score,
            ai_explanation=ai_explanation,
            calculated_at=datetime.now(timezone.utc),
            is_demo=True,
            **sub_scores,
        )

    @staticmethod
    def ceo_briefing() -> CEOBriefingOut:
        return CEOBriefingOut(
            id=_DEMO_BRIEFING_ID,
            finding=f"{DemoDataService.BUSINESS_NAME}'s subscription renewals are up 18% this month.",
            why=[
                "Renewal rate for existing subscribers climbed from 71% to 84% over the past four weeks.",
                "Two new subscription tiers launched last month already account for a quarter of all renewals.",
                "Customer support response time improved, cutting cancellation requests tied to complaints.",
            ],
            recommendation=(
                "Double down on the two new subscription tiers with a limited-time referral bonus "
                "while renewal momentum is high."
            ),
            confidence="high",
            is_read=False,
            generated_at=datetime.now(timezone.utc),
            is_demo=True,
        )

    @staticmethod
    def business_analytics(days: int = 90) -> BusinessAnalyticsOut:
        # Local Random instance (not the module-level `random.seed()`) so
        # this doesn't reset global random state for anything else running
        # in the same process - only this generator is deterministic.
        rng = random.Random(_DEMO_SEED)

        window = min(days, _DEMO_ANALYTICS_WINDOW_DAYS)
        today = datetime.now(timezone.utc).date()

        revenue_over_time: list[RevenuePoint] = []
        task_completion_over_time: list[TaskCompletionPoint] = []
        for i in range(window):
            day = today - timedelta(days=window - 1 - i)
            progress = i / max(window - 1, 1)

            base_revenue = 180 + progress * 160  # ~$180/day trending to ~$340/day
            amount = round(base_revenue * rng.uniform(0.88, 1.12), 2)
            revenue_over_time.append(RevenuePoint(period=day, amount=amount))

            created = rng.randint(1, 3)
            completion_chance = 0.55 + progress * 0.3
            completed = sum(1 for _ in range(created) if rng.random() < completion_chance)
            task_completion_over_time.append(
                TaskCompletionPoint(period=day, created=created, completed=completed)
            )

        # Last point matches health_score()'s overall_score so the two
        # endpoints tell the same story instead of drifting by a point.
        weekly_scores = [58, 64, 69, DemoDataService.health_score().overall_score]
        health_score_history: list[HealthScorePoint] = [
            HealthScorePoint(
                calculated_at=today - timedelta(days=(len(weekly_scores) - 1 - week) * 7),
                overall_score=score,
            )
            for week, score in enumerate(weekly_scores)
        ]

        return BusinessAnalyticsOut(
            revenue_over_time=revenue_over_time,
            task_completion_over_time=task_completion_over_time,
            health_score_history=health_score_history,
            is_demo=True,
        )
