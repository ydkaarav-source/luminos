"""
Health Score calculation.

MVP scoring is rule-based (deterministic, explainable) using signals
already in the DB - revenue recency/consistency, task completion rate,
project activity, and onboarding-declared challenges. The AI layer is
only used to *explain* the score in plain language, not to compute it -
keeping the number itself auditable and reproducible.
"""
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.ai_conversation import ConversationContext
from app.models.business import Business
from app.models.health_score import HealthScore
from app.models.revenue_entry import RevenueEntry
from app.models.task import Task, TaskStatus
from app.services.ai.ai_orchestrator import AIOrchestrator
from app.services.ai.prompt_templates import health_score_explainer as prompt_template


class HealthScoreService:
    def __init__(self, db: Session):
        self.db = db
        self.ai = AIOrchestrator(db)

    def get_latest(self, business_id: UUID) -> HealthScore | None:
        return (
            self.db.query(HealthScore)
            .filter(HealthScore.business_id == business_id)
            .order_by(HealthScore.calculated_at.desc())
            .first()
        )

    def get_history(self, business_id: UUID, limit: int = 30) -> list[HealthScore]:
        return (
            self.db.query(HealthScore)
            .filter(HealthScore.business_id == business_id)
            .order_by(HealthScore.calculated_at.desc())
            .limit(limit)
            .all()
        )

    async def recalculate(self, business: Business, user_id: UUID) -> HealthScore:
        scores = self._compute_rule_based_scores(business)

        memory_lines = self.ai.get_memory_context(business.id)
        system_prompt, user_prompt = prompt_template.build_prompt(scores, memory_lines)

        raw = await self.ai.run(
            business_id=business.id,
            user_id=user_id,
            context_type=ConversationContext.HEALTH_SCORE,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_mode=True,
        )
        explanation = self.ai.run_json(raw)

        record = HealthScore(business_id=business.id, ai_explanation=explanation, **scores)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def _compute_rule_based_scores(self, business: Business) -> dict:
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)

        # Revenue: consistency + recency of logged revenue entries.
        recent_revenue_count = (
            self.db.query(RevenueEntry)
            .filter(RevenueEntry.business_id == business.id, RevenueEntry.entry_date >= thirty_days_ago)
            .count()
        )
        revenue_score = min(100, recent_revenue_count * 10) if recent_revenue_count else 20

        # Operations: task completion rate over the last 30 days.
        total_recent_tasks = (
            self.db.query(Task)
            .filter(Task.business_id == business.id, Task.created_at >= thirty_days_ago)
            .count()
        )
        completed_recent_tasks = (
            self.db.query(Task)
            .filter(
                Task.business_id == business.id,
                Task.status == TaskStatus.DONE,
                Task.created_at >= thirty_days_ago,
            )
            .count()
        )
        operations_score = (
            int((completed_recent_tasks / total_recent_tasks) * 100) if total_recent_tasks else 40
        )

        # Marketing / customer growth / financial management: MVP placeholders
        # derived from stage + declared challenges until dedicated tracking
        # (CRM, ad spend, etc.) exists. Kept explicit rather than hidden.
        challenge_penalty = len(business.current_challenges or []) * 5
        marketing_score = max(10, 55 - challenge_penalty)
        customer_growth_score = max(10, 50 - challenge_penalty)
        financial_management_score = max(10, 60 - challenge_penalty)

        overall_score = round(
            (
                revenue_score
                + operations_score
                + marketing_score
                + customer_growth_score
                + financial_management_score
            )
            / 5
        )

        return {
            "overall_score": overall_score,
            "revenue_score": revenue_score,
            "operations_score": operations_score,
            "marketing_score": marketing_score,
            "customer_growth_score": customer_growth_score,
            "financial_management_score": financial_management_score,
        }
