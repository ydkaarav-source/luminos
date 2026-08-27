import json
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import GoogleCalendarError
from app.core.logging import get_logger
from app.models.ai_conversation import ConversationContext
from app.models.ai_insight import AIInsight, InsightPriority, InsightType
from app.models.business import Business
from app.models.task import Task, TaskStatus
from app.repositories.business_profile_repository import BusinessProfileRepository
from app.services.ai.ai_orchestrator import AIOrchestrator
from app.services.ai.prompt_templates import ceo_briefing as prompt_template
from app.services.business_metrics_service import BusinessMetricsService
from app.services.google_calendar_service import GoogleCalendarService
from app.services.health_score_service import HealthScoreService

logger = get_logger(__name__)


class CEOBriefingService:
    def __init__(self, db: Session):
        self.db = db
        self.ai = AIOrchestrator(db)
        self.health_score_service = HealthScoreService(db)
        self.business_profiles = BusinessProfileRepository(db)
        self.google_calendar = GoogleCalendarService(db)
        self.metrics = BusinessMetricsService(db)

    def get_today(self, business_id: UUID) -> AIInsight | None:
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        return (
            self.db.query(AIInsight)
            .filter(
                AIInsight.business_id == business_id,
                AIInsight.insight_type == InsightType.CEO_BRIEFING,
                AIInsight.generated_at >= today_start,
            )
            .order_by(AIInsight.generated_at.desc())
            .first()
        )

    def get_history(self, business_id: UUID, limit: int = 14) -> list[AIInsight]:
        return (
            self.db.query(AIInsight)
            .filter(AIInsight.business_id == business_id, AIInsight.insight_type == InsightType.CEO_BRIEFING)
            .order_by(AIInsight.generated_at.desc())
            .limit(limit)
            .all()
        )

    async def generate_today(self, business: Business, user_id: UUID) -> AIInsight:
        existing = self.get_today(business.id)
        if existing:
            return existing

        metrics = await self._gather_metrics(business)

        memory_lines = self.ai.get_memory_context(business.id)
        system_prompt, user_prompt = prompt_template.build_prompt(business.name, metrics, memory_lines)

        raw = await self.ai.run(
            business_id=business.id,
            user_id=user_id,
            context_type=ConversationContext.CEO_BRIEFING,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_mode=True,
        )
        parsed = self.ai.run_json(raw)

        # AIInsight's existing columns hold this structured content without
        # a migration: title = the finding headline, body = JSON-encoded
        # {why, recommendation}, priority = confidence (same "low"/
        # "medium"/"high" value domain, reused only for CEO Briefing rows -
        # other insight types still use `priority` in its original sense).
        finding = parsed["finding"]
        title = finding[:197] + "..." if len(finding) > 200 else finding
        insight = AIInsight(
            business_id=business.id,
            insight_type=InsightType.CEO_BRIEFING,
            title=title,
            body=json.dumps({"why": parsed["why"], "recommendation": parsed["recommendation"]}),
            priority=InsightPriority(parsed.get("confidence", "medium")),
        )
        self.db.add(insight)
        self.db.commit()
        self.db.refresh(insight)
        return insight

    def mark_read(self, insight: AIInsight) -> AIInsight:
        insight.is_read = True
        self.db.add(insight)
        self.db.commit()
        self.db.refresh(insight)
        return insight

    async def _gather_metrics(self, business: Business) -> dict:
        """
        All the real numbers behind today's briefing, computed here so the
        AI reasons about them rather than estimating them itself - same
        split as Health Score: code computes, AI explains.
        """
        now = datetime.now(timezone.utc)

        # Revenue: this week vs. the week before - computed once in
        # BusinessMetricsService so this and the Opportunity Radar never
        # disagree about what "this week's revenue" means.
        revenue = self.metrics.revenue_week_over_week(business.id)
        revenue_this_week = revenue["this_week"]
        revenue_last_week = revenue["last_week"]
        revenue_change_pct = revenue["change_pct"]

        # Tasks: yesterday's completions, the same 24h window one week ago
        # for comparison, and overdue open tasks - a real signal that
        # wasn't surfaced anywhere before. "Open" matches the status set
        # already used below for open_priority_tasks (todo/in_progress).
        yesterday_start = now - timedelta(days=1)
        tasks_completed_yesterday = (
            self.db.query(Task)
            .filter(
                Task.business_id == business.id,
                Task.status == TaskStatus.DONE,
                Task.completed_at >= yesterday_start,
            )
            .count()
        )
        same_weekday_last_week_start = now - timedelta(days=8)
        tasks_completed_same_weekday_last_week = (
            self.db.query(Task)
            .filter(
                Task.business_id == business.id,
                Task.status == TaskStatus.DONE,
                Task.completed_at >= same_weekday_last_week_start,
                Task.completed_at < yesterday_start,
            )
            .count()
        )
        # Same shared overdue-tasks query the Opportunity Radar uses -
        # see business_metrics_service.py.
        overdue_tasks_count = len(self.metrics.overdue_tasks(business.id))
        open_priority_tasks = [
            t.title
            for t in self.db.query(Task)
            .filter(
                Task.business_id == business.id,
                Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS]),
            )
            .order_by(Task.priority.desc(), Task.due_date.asc().nulls_last())
            .limit(3)
            .all()
        ]

        # Health Score: latest value plus the delta from the calculation
        # before it, if one exists.
        score_history = self.health_score_service.get_history(business.id, limit=2)
        latest_health_score = score_history[0].overall_score if score_history else None
        health_score_delta = (
            score_history[0].overall_score - score_history[1].overall_score
            if len(score_history) > 1
            else None
        )

        # Business Brain profile, if the founder has filled one in.
        profile = self.business_profiles.get_by_business_id(business.id)
        business_profile = (
            {
                "industry": profile.industry,
                "description": profile.description,
                "target_customers": profile.target_customers,
                "company_goals": profile.company_goals,
            }
            if profile
            else None
        )

        return {
            "revenue_this_week": revenue_this_week,
            "revenue_last_week": revenue_last_week,
            "revenue_change_pct": revenue_change_pct,
            "tasks_completed_yesterday": tasks_completed_yesterday,
            "tasks_completed_same_weekday_last_week": tasks_completed_same_weekday_last_week,
            "overdue_tasks_count": overdue_tasks_count,
            "open_priority_tasks": open_priority_tasks,
            "latest_health_score": latest_health_score,
            "health_score_delta": health_score_delta,
            "business_profile": business_profile,
            "todays_calendar_events": await self._get_todays_calendar_events(business.id),
        }

    async def _get_todays_calendar_events(self, business_id: UUID) -> list[dict] | None:
        """
        None means "no calendar context at all" (not connected, or the
        connection is currently broken) - the prompt template treats that
        as additive-and-absent, never a reason to fail the briefing. An
        empty list is a real, meaningful answer ("connected, zero events
        today"), which is different from not being connected at all.
        """
        status = self.google_calendar.get_status(business_id)
        if not status["connected"]:
            return None

        try:
            events = await self.google_calendar.get_upcoming_events(business_id)
        except GoogleCalendarError:
            # A broken calendar connection (revoked access, Google API
            # hiccup, etc.) must never take down CEO Briefing generation -
            # same principle as "no connection at all": additive context
            # only, never a hard dependency.
            logger.warning("Google Calendar fetch failed for business %s; omitting from briefing", business_id)
            return None

        today = datetime.now(timezone.utc).date()
        return [e for e in events if e["start"] and e["start"][:10] == today.isoformat()]
