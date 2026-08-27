"""
Rule-based Opportunity/Risk Radar - LuminOS's first PROACTIVE feature.
Every other AI feature (CEO Briefing, Health Score, the Assistant) is
reactive: generated only when the founder asks, or once a day on
request. This runs on its own schedule (see core/scheduler.py) and
surfaces findings without anyone asking.

Deliberately zero AI calls: every finding here is a deterministic
threshold check against real data, re-runnable and reproducible - the
same discipline Health Score's numeric scores already follow (code
computes, not an AI guess). AI-written explanations for these findings
are an intentional fast-follow, out of scope here.

Supersession: at most one UNDISMISSED finding per (business,
finding_type) at a time - a scheduler run that sees the same condition
again is a no-op, not a duplicate row. Dismissing a finding fully
reopens detection for that type - if the underlying condition is still
(or again) true on a later run, a fresh finding gets created. No
separate "resolved" state: dismiss is the only way a finding stops
being active, whether the founder dismissed it because they fixed the
issue or because they've simply seen it.
"""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import case
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.opportunity_finding import (
    OpportunityFinding,
    OpportunityFindingSeverity,
    OpportunityFindingType,
)
from app.models.revenue_entry import RevenueEntry, RevenueEntryOrigin
from app.models.stripe_connection import StripeConnection
from app.models.website_brief import WebsiteBrief
from app.services.business_metrics_service import BusinessMetricsService

# --- Thresholds - real product decisions, not arbitrary values. See
# this task's final report for the reasoning behind each one. ---
REVENUE_DROP_PCT_THRESHOLD = -25.0
REVENUE_DROP_HIGH_SEVERITY_PCT = -50.0
REVENUE_STREAK_MIN_WEEKS = 3
TASK_OVERDUE_DAYS_THRESHOLD = 3
TASK_OVERDUE_HIGH_SEVERITY_DAYS = 14
STRIPE_SYNC_STALE_HOURS = 24


class OpportunityRadarService:
    def __init__(self, db: Session):
        self.db = db
        self.metrics = BusinessMetricsService(db)

    def run_checks(self, business_id: UUID) -> list[OpportunityFinding]:
        """
        Runs every check for one business. Returns only the findings
        NEWLY created this run - callers that want the full open list
        should use get_active() instead (see GET /opportunities).
        """
        created = []
        for check in (
            self._check_revenue_drop,
            self._check_revenue_streak,
            self._check_task_overdue,
            self._check_website_not_connected,
            self._check_stripe_sync_stale,
        ):
            finding = check(business_id)
            if finding:
                created.append(finding)
        return created

    def get_active(self, business_id: UUID) -> list[OpportunityFinding]:
        severity_order = case(
            (OpportunityFinding.severity == OpportunityFindingSeverity.HIGH, 0),
            (OpportunityFinding.severity == OpportunityFindingSeverity.MEDIUM, 1),
            (OpportunityFinding.severity == OpportunityFindingSeverity.LOW, 2),
        )
        return (
            self.db.query(OpportunityFinding)
            .filter(OpportunityFinding.business_id == business_id, OpportunityFinding.is_dismissed.is_(False))
            .order_by(severity_order, OpportunityFinding.detected_at.desc())
            .all()
        )

    def dismiss(self, finding_id: UUID, business_id: UUID) -> OpportunityFinding:
        finding = self.db.get(OpportunityFinding, finding_id)
        if not finding or finding.business_id != business_id:
            raise NotFoundError("Finding not found.")
        finding.is_dismissed = True
        finding.dismissed_at = datetime.now(timezone.utc)
        self.db.add(finding)
        self.db.commit()
        self.db.refresh(finding)
        return finding

    # --- Checks ---

    def _check_revenue_drop(self, business_id: UUID) -> OpportunityFinding | None:
        revenue = self.metrics.revenue_week_over_week(business_id)
        change_pct = revenue["change_pct"]
        if change_pct is None or change_pct > REVENUE_DROP_PCT_THRESHOLD:
            return None
        title = f"Revenue dropped {abs(change_pct):.0f}% this week"
        severity = (
            OpportunityFindingSeverity.HIGH
            if change_pct <= REVENUE_DROP_HIGH_SEVERITY_PCT
            else OpportunityFindingSeverity.MEDIUM
        )
        return self._create_if_new(
            business_id,
            OpportunityFindingType.REVENUE_DROP,
            severity,
            title,
            {"this_week": revenue["this_week"], "last_week": revenue["last_week"], "percent_change": change_pct},
        )

    def _check_revenue_streak(self, business_id: UUID) -> OpportunityFinding | None:
        totals = self.metrics.weekly_revenue_totals(business_id, weeks=REVENUE_STREAK_MIN_WEEKS + 1)
        if any(t <= 0 for t in totals):
            return None
        if not all(totals[i] < totals[i + 1] for i in range(len(totals) - 1)):
            return None
        title = f"Revenue has grown for {REVENUE_STREAK_MIN_WEEKS} straight weeks, now ${totals[-1]:,.2f}/week"
        return self._create_if_new(
            business_id,
            OpportunityFindingType.REVENUE_STREAK,
            OpportunityFindingSeverity.LOW,
            title,
            {"weekly_totals": totals},
        )

    def _check_task_overdue(self, business_id: UUID) -> OpportunityFinding | None:
        today = datetime.now(timezone.utc).date()
        badly_overdue = [
            t for t in self.metrics.overdue_tasks(business_id) if (today - t.due_date).days > TASK_OVERDUE_DAYS_THRESHOLD
        ]
        if not badly_overdue:
            return None
        worst = max(badly_overdue, key=lambda t: (today - t.due_date).days)
        days_overdue = (today - worst.due_date).days
        title = (
            f"'{worst.title}' is {days_overdue} days overdue"
            if len(badly_overdue) == 1
            else f"{len(badly_overdue)} tasks are more than {TASK_OVERDUE_DAYS_THRESHOLD} days overdue"
        )
        severity = (
            OpportunityFindingSeverity.HIGH
            if days_overdue > TASK_OVERDUE_HIGH_SEVERITY_DAYS
            else OpportunityFindingSeverity.MEDIUM
        )
        return self._create_if_new(
            business_id,
            OpportunityFindingType.TASK_OVERDUE,
            severity,
            title,
            {
                "overdue_task_count": len(badly_overdue),
                "most_overdue_days": days_overdue,
                "most_overdue_title": worst.title,
            },
        )

    def _check_website_not_connected(self, business_id: UUID) -> OpportunityFinding | None:
        brief = (
            self.db.query(WebsiteBrief)
            .filter(WebsiteBrief.business_id == business_id)
            .order_by(WebsiteBrief.created_at.desc())
            .first()
        )
        if not brief or brief.site_url:
            return None
        title = "Website brief generated, but no live site connected yet"
        return self._create_if_new(
            business_id,
            OpportunityFindingType.WEBSITE_NOT_CONNECTED,
            OpportunityFindingSeverity.LOW,
            title,
            {"website_brief_id": str(brief.id), "website_brief_title": brief.title},
        )

    def _check_stripe_sync_stale(self, business_id: UUID) -> OpportunityFinding | None:
        connection = (
            self.db.query(StripeConnection).filter(StripeConnection.business_id == business_id).first()
        )
        if not connection:
            return None

        latest_synced = (
            self.db.query(RevenueEntry)
            .filter(RevenueEntry.business_id == business_id, RevenueEntry.origin == RevenueEntryOrigin.STRIPE)
            .order_by(RevenueEntry.created_at.desc())
            .first()
        )
        # No synced entry at all yet is different from "sync went stale
        # after previously working" - fall back to connected_at so a
        # freshly-connected account isn't immediately flagged stale
        # before its first sync has even had a chance to run.
        reference_time = latest_synced.created_at if latest_synced else connection.connected_at
        age_hours = (datetime.now(timezone.utc) - reference_time).total_seconds() / 3600
        if age_hours < STRIPE_SYNC_STALE_HOURS:
            return None

        title = f"Stripe hasn't synced new revenue in {int(age_hours)} hours"
        return self._create_if_new(
            business_id,
            OpportunityFindingType.STRIPE_SYNC_STALE,
            OpportunityFindingSeverity.MEDIUM,
            title,
            {"hours_since_last_sync": round(age_hours, 1), "last_synced_at": reference_time.isoformat()},
        )

    def _create_if_new(
        self,
        business_id: UUID,
        finding_type: OpportunityFindingType,
        severity: OpportunityFindingSeverity,
        title: str,
        details: dict,
    ) -> OpportunityFinding | None:
        existing = (
            self.db.query(OpportunityFinding)
            .filter(
                OpportunityFinding.business_id == business_id,
                OpportunityFinding.finding_type == finding_type,
                OpportunityFinding.is_dismissed.is_(False),
            )
            .first()
        )
        if existing:
            return None

        finding = OpportunityFinding(
            business_id=business_id,
            finding_type=finding_type,
            severity=severity,
            title=title,
            details=details,
        )
        self.db.add(finding)
        self.db.commit()
        self.db.refresh(finding)
        return finding
