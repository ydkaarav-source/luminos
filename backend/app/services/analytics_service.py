from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.health_score import HealthScore
from app.models.revenue_entry import RevenueEntry
from app.models.task import Task, TaskStatus
from app.schemas.analytics import (
    BusinessAnalyticsOut,
    HealthScorePoint,
    RevenuePoint,
    TaskCompletionPoint,
)


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_business_analytics(self, business_id: UUID, days: int = 90) -> BusinessAnalyticsOut:
        return BusinessAnalyticsOut(
            revenue_over_time=self._revenue_over_time(business_id, days),
            task_completion_over_time=self._task_completion_over_time(business_id, days),
            health_score_history=self._health_score_history(business_id, days),
        )

    def _revenue_over_time(self, business_id: UUID, days: int) -> list[RevenuePoint]:
        rows = (
            self.db.query(
                RevenueEntry.entry_date.label("period"),
                func.sum(RevenueEntry.amount).label("amount"),
            )
            .filter(RevenueEntry.business_id == business_id)
            .group_by(RevenueEntry.entry_date)
            .order_by(RevenueEntry.entry_date.asc())
            .all()
        )
        return [RevenuePoint(period=r.period, amount=float(r.amount)) for r in rows]

    def _task_completion_over_time(self, business_id: UUID, days: int) -> list[TaskCompletionPoint]:
        created_rows = (
            self.db.query(
                func.date(Task.created_at).label("period"),
                func.count(Task.id).label("created"),
            )
            .filter(Task.business_id == business_id)
            .group_by(func.date(Task.created_at))
            .all()
        )
        completed_rows = (
            self.db.query(
                func.date(Task.completed_at).label("period"),
                func.count(Task.id).label("completed"),
            )
            .filter(Task.business_id == business_id, Task.status == TaskStatus.DONE)
            .group_by(func.date(Task.completed_at))
            .all()
        )

        by_period: dict = {}
        for r in created_rows:
            by_period.setdefault(r.period, {"created": 0, "completed": 0})["created"] = r.created
        for r in completed_rows:
            if r.period:
                by_period.setdefault(r.period, {"created": 0, "completed": 0})["completed"] = r.completed

        return [
            TaskCompletionPoint(period=period, created=v["created"], completed=v["completed"])
            for period, v in sorted(by_period.items())
        ]

    def _health_score_history(self, business_id: UUID, days: int) -> list[HealthScorePoint]:
        rows = (
            self.db.query(HealthScore)
            .filter(HealthScore.business_id == business_id)
            .order_by(HealthScore.calculated_at.asc())
            .all()
        )
        return [
            HealthScorePoint(calculated_at=r.calculated_at.date(), overall_score=r.overall_score)
            for r in rows
        ]