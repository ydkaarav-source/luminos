from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.ai_conversation import ConversationContext
from app.models.ai_insight import AIInsight, InsightPriority, InsightType
from app.models.business import Business
from app.models.task import Task, TaskStatus
from app.services.ai.ai_orchestrator import AIOrchestrator
from app.services.ai.prompt_templates import ceo_briefing as prompt_template
from app.services.health_score_service import HealthScoreService


class CEOBriefingService:
    def __init__(self, db: Session):
        self.db = db
        self.ai = AIOrchestrator(db)
        self.health_score_service = HealthScoreService(db)

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

        yesterday_start = datetime.now(timezone.utc) - timedelta(days=1)
        tasks_completed_yesterday = (
            self.db.query(Task)
            .filter(
                Task.business_id == business.id,
                Task.status == TaskStatus.DONE,
                Task.completed_at >= yesterday_start,
            )
            .count()
        )
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
        latest_score = self.health_score_service.get_latest(business.id)

        memory_lines = self.ai.get_memory_context(business.id)
        system_prompt, user_prompt = prompt_template.build_prompt(
            business.name,
            tasks_completed_yesterday,
            open_priority_tasks,
            latest_score.overall_score if latest_score else None,
            memory_lines,
        )

        raw = await self.ai.run(
            business_id=business.id,
            user_id=user_id,
            context_type=ConversationContext.CEO_BRIEFING,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_mode=True,
        )
        parsed = self.ai.run_json(raw)

        insight = AIInsight(
            business_id=business.id,
            insight_type=InsightType.CEO_BRIEFING,
            title=parsed["title"],
            body=parsed["body"],
            priority=InsightPriority(parsed.get("priority", "medium")),
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
