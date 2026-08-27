"""
Shared, deterministic business metrics - revenue and task numbers
computed here once so CEO Briefing and the Opportunity Radar never
silently disagree about what "this week's revenue" or "overdue tasks"
means. Both features import this rather than each computing their own
slightly-different version of the same math (this was extracted out of
CEOBriefingService, which originally computed these inline).
"""
from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.revenue_entry import RevenueEntry
from app.models.task import Task, TaskStatus


class BusinessMetricsService:
    def __init__(self, db: Session):
        self.db = db

    def sum_revenue(self, business_id: UUID, start_date: date, end_date: date) -> float:
        total = (
            self.db.query(func.sum(RevenueEntry.amount))
            .filter(
                RevenueEntry.business_id == business_id,
                RevenueEntry.entry_date >= start_date,
                RevenueEntry.entry_date < end_date,
            )
            .scalar()
        )
        return float(total) if total is not None else 0.0

    def revenue_week_over_week(self, business_id: UUID) -> dict:
        """
        This week (last 7 days) vs. the 7 days before that, plus the
        percent change - None when there's no prior-week revenue to
        compare against (division by zero would otherwise be undefined,
        not just "0%").
        """
        today = datetime.now(timezone.utc).date()
        week_start = today - timedelta(days=7)
        prior_week_start = today - timedelta(days=14)

        this_week = self.sum_revenue(business_id, week_start, today)
        last_week = self.sum_revenue(business_id, prior_week_start, week_start)
        change_pct = round(((this_week - last_week) / last_week) * 100, 1) if last_week else None

        return {"this_week": this_week, "last_week": last_week, "change_pct": change_pct}

    def weekly_revenue_totals(self, business_id: UUID, weeks: int) -> list[float]:
        """
        `weeks` rolling 7-day totals ending today, oldest first - rolling
        windows (not calendar weeks), consistent with revenue_week_over_week's
        own "last 7 days" definition, so a streak here means the same
        week-over-week comparison stayed positive for `weeks` checks running.
        """
        today = datetime.now(timezone.utc).date()
        totals = []
        for i in range(weeks):
            end = today - timedelta(days=7 * i)
            start = end - timedelta(days=7)
            totals.append(self.sum_revenue(business_id, start, end))
        totals.reverse()
        return totals

    def overdue_tasks(self, business_id: UUID) -> list[Task]:
        today = datetime.now(timezone.utc).date()
        return (
            self.db.query(Task)
            .filter(
                Task.business_id == business_id,
                Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS]),
                Task.due_date < today,
            )
            .all()
        )
