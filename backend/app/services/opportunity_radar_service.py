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
separate "resolved" state at the dismiss level: dismiss is how a
finding stops being ACTIVE, whether the founder dismissed it because
they fixed the issue or because they've simply seen it.

Resolution tracking (this app's first "closed loop" capability) is a
separate lifecycle stage on top of that: independent of is_dismissed,
every OPEN finding (resolved_at is null) gets periodically re-checked
against the SAME threshold logic used for detection - see
check_resolutions and _evaluators below. This only ever records that a
flagged condition was later observed to no longer be true; it never
claims LuminOS caused that change.

One finding type, WEBSITE_CONTENT_CHANGED (see
check_website_content_changed), doesn't fit that state-threshold model
at all - a site's content changing is a one-time event, not an ongoing
condition that can later become "not true" again, so it's intentionally
excluded from resolution tracking; dismissing is its only close.
"""
import hashlib
import re
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import case
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, WebsiteUnreachableError
from app.core.logging import get_logger
from app.models.opportunity_finding import (
    OpportunityFinding,
    OpportunityFindingSeverity,
    OpportunityFindingType,
)
from app.models.revenue_entry import RevenueEntry, RevenueEntryOrigin
from app.models.stripe_connection import StripeConnection
from app.models.website_brief import WebsiteBrief
from app.services.business_metrics_service import BusinessMetricsService
from app.services.website_scraper_service import WebsiteScraperService

logger = get_logger(__name__)

# Reduces false positives before hashing - imperfect by design, not a
# general-purpose diff tool. Only strips a year immediately following an
# explicit ©/"copyright" marker (the single most common auto-updating
# footer text), not any bare 4-digit number - a real price or year
# mentioned elsewhere in the page must never be silently erased. This
# intentionally does NOT catch every form of "dynamic" content (a bare
# year with no ©/"copyright" marker, a "last updated" timestamp in
# prose, a visitor counter) - those still register as a real content
# change. That's an honest limitation of a cheap regex approach, not a
# silent gap - see this task's final report.
_COPYRIGHT_YEAR_RE = re.compile(r"(?:©|copyright)\s*\d{4}(?:\s*[-–]\s*\d{4})?", re.IGNORECASE)


def _normalize_for_hash(text: str) -> str:
    # Lowercased so a pure casing change (e.g. a heading's capitalization)
    # isn't flagged as new content - re-collapse whitespace afterward
    # since substitution can leave behind doubled spaces.
    normalized = _COPYRIGHT_YEAR_RE.sub("", text.lower())
    return re.sub(r"\s+", " ", normalized).strip()


def _hash_content(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# --- Thresholds - real product decisions, not arbitrary values. See
# this task's final report for the reasoning behind each one. ---
REVENUE_DROP_PCT_THRESHOLD = -25.0
REVENUE_DROP_HIGH_SEVERITY_PCT = -50.0
REVENUE_STREAK_MIN_WEEKS = 3
TASK_OVERDUE_DAYS_THRESHOLD = 3
TASK_OVERDUE_HIGH_SEVERITY_DAYS = 14
STRIPE_SYNC_STALE_HOURS = 24

# A finding needs at least this long to meaningfully re-evaluate - the
# checks themselves are daily-grained (week-over-week revenue, days-
# overdue tasks, hours-since-sync in 24h units), so re-checking sooner
# couldn't show a genuine change either way.
MIN_RESOLUTION_CHECK_AGE_HOURS = 24


class OpportunityRadarService:
    def __init__(self, db: Session):
        self.db = db
        self.metrics = BusinessMetricsService(db)
        self.scraper = WebsiteScraperService()
        # One dispatch table, built once, reused by both detection
        # (indirectly, via each _check_* method) and resolution-checking
        # (directly, in check_resolutions) - this is what guarantees the
        # two can never silently disagree about what "still true" means.
        self._evaluators = {
            OpportunityFindingType.REVENUE_DROP: (
                self._current_revenue_drop_values,
                self._revenue_drop_condition,
            ),
            OpportunityFindingType.REVENUE_STREAK: (
                self._current_revenue_streak_values,
                self._revenue_streak_condition,
            ),
            OpportunityFindingType.TASK_OVERDUE: (
                self._current_task_overdue_values,
                self._task_overdue_condition,
            ),
            OpportunityFindingType.WEBSITE_NOT_CONNECTED: (
                self._current_website_values,
                self._website_not_connected_condition,
            ),
            OpportunityFindingType.STRIPE_SYNC_STALE: (
                self._current_stripe_sync_values,
                self._stripe_sync_stale_condition,
            ),
        }
        self._resolution_notes = {
            OpportunityFindingType.REVENUE_DROP: self._resolution_note_revenue_drop,
            OpportunityFindingType.REVENUE_STREAK: self._resolution_note_revenue_streak,
            OpportunityFindingType.TASK_OVERDUE: self._resolution_note_task_overdue,
            OpportunityFindingType.WEBSITE_NOT_CONNECTED: self._resolution_note_website,
            OpportunityFindingType.STRIPE_SYNC_STALE: self._resolution_note_stripe_sync,
        }

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

    def check_resolutions(self, business_id: UUID) -> list[OpportunityFinding]:
        """
        Re-evaluates every OPEN finding (resolved_at is null) for this
        business that's at least MIN_RESOLUTION_CHECK_AGE_HOURS old,
        using the exact same evaluator + condition pair detection uses
        for that finding_type - deliberately not is_dismissed-filtered,
        since a founder may have dismissed a finding while still wanting
        to know later whether it resolved.

        Confirmed-resolved findings (condition now false) get
        resolved_at set and a plain, non-AI resolution_note built from
        the finding's own stored `details` (before) vs. a fresh
        evaluation (after). Still-true findings are left untouched -
        this is a no-op for them, not an error.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=MIN_RESOLUTION_CHECK_AGE_HOURS)
        open_findings = (
            self.db.query(OpportunityFinding)
            .filter(
                OpportunityFinding.business_id == business_id,
                OpportunityFinding.resolved_at.is_(None),
                OpportunityFinding.detected_at <= cutoff,
            )
            .all()
        )

        resolved = []
        for finding in open_findings:
            evaluator = self._evaluators.get(finding.finding_type)
            if evaluator is None:
                # Not every finding_type has a re-checkable threshold
                # condition - WEBSITE_CONTENT_CHANGED reports a one-time
                # event (content changed), not an ongoing state that can
                # revert to "not true". Dismissing is the only way those
                # findings close.
                continue
            current_values_fn, condition_fn = evaluator
            current_values = current_values_fn(business_id)
            if condition_fn(current_values):
                continue  # still true - no change

            note_builder = self._resolution_notes[finding.finding_type]
            finding.resolved_at = datetime.now(timezone.utc)
            finding.resolution_note = note_builder(finding.details, current_values)
            self.db.add(finding)
            resolved.append(finding)

        if resolved:
            self.db.commit()
            for f in resolved:
                self.db.refresh(f)
        return resolved

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

    def get_recently_resolved(self, business_id: UUID, days: int = 14) -> list[OpportunityFinding]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return (
            self.db.query(OpportunityFinding)
            .filter(
                OpportunityFinding.business_id == business_id,
                OpportunityFinding.resolved_at.isnot(None),
                OpportunityFinding.resolved_at >= cutoff,
            )
            .order_by(OpportunityFinding.resolved_at.desc())
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

    # --- Checks: each pairs a "current values" evaluator (always
    # returns the real current numbers) with a "condition" predicate
    # (decides whether those numbers cross the threshold). Detection
    # and resolution-checking both call the SAME pair per finding_type -
    # see _evaluators above - so they can never disagree about what
    # "still true" means. ---

    def _current_revenue_drop_values(self, business_id: UUID) -> dict:
        revenue = self.metrics.revenue_week_over_week(business_id)
        return {
            "this_week": revenue["this_week"],
            "last_week": revenue["last_week"],
            "percent_change": revenue["change_pct"],
        }

    def _revenue_drop_condition(self, values: dict) -> bool:
        pct = values["percent_change"]
        return pct is not None and pct <= REVENUE_DROP_PCT_THRESHOLD

    def _check_revenue_drop(self, business_id: UUID) -> OpportunityFinding | None:
        values = self._current_revenue_drop_values(business_id)
        if not self._revenue_drop_condition(values):
            return None
        change_pct = values["percent_change"]
        title = f"Revenue dropped {abs(change_pct):.0f}% this week"
        severity = (
            OpportunityFindingSeverity.HIGH
            if change_pct <= REVENUE_DROP_HIGH_SEVERITY_PCT
            else OpportunityFindingSeverity.MEDIUM
        )
        return self._create_if_new(business_id, OpportunityFindingType.REVENUE_DROP, severity, title, values)

    def _resolution_note_revenue_drop(self, before: dict, after: dict) -> str:
        return (
            f"Revenue recovered to ${after['this_week']:,.2f} this week, "
            f"up from the ${before['this_week']:,.2f} that triggered this finding."
        )

    def _current_revenue_streak_values(self, business_id: UUID) -> dict:
        totals = self.metrics.weekly_revenue_totals(business_id, weeks=REVENUE_STREAK_MIN_WEEKS + 1)
        return {"weekly_totals": totals}

    def _revenue_streak_condition(self, values: dict) -> bool:
        totals = values["weekly_totals"]
        if any(t <= 0 for t in totals):
            return False
        return all(totals[i] < totals[i + 1] for i in range(len(totals) - 1))

    def _check_revenue_streak(self, business_id: UUID) -> OpportunityFinding | None:
        values = self._current_revenue_streak_values(business_id)
        if not self._revenue_streak_condition(values):
            return None
        totals = values["weekly_totals"]
        title = f"Revenue has grown for {REVENUE_STREAK_MIN_WEEKS} straight weeks, now ${totals[-1]:,.2f}/week"
        return self._create_if_new(
            business_id, OpportunityFindingType.REVENUE_STREAK, OpportunityFindingSeverity.LOW, title, values
        )

    def _resolution_note_revenue_streak(self, before: dict, after: dict) -> str:
        # A "resolved" streak just means it stopped continuing - not a
        # problem fixed, so this is worded neutrally rather than as good
        # or bad news either way.
        return (
            f"The revenue growth streak flagged earlier is no longer continuing - "
            f"this week's revenue is ${after['weekly_totals'][-1]:,.2f}."
        )

    def _current_task_overdue_values(self, business_id: UUID) -> dict:
        today = datetime.now(timezone.utc).date()
        badly_overdue = [
            t
            for t in self.metrics.overdue_tasks(business_id)
            if (today - t.due_date).days > TASK_OVERDUE_DAYS_THRESHOLD
        ]
        if not badly_overdue:
            return {"overdue_task_count": 0, "most_overdue_days": 0, "most_overdue_title": None}
        worst = max(badly_overdue, key=lambda t: (today - t.due_date).days)
        return {
            "overdue_task_count": len(badly_overdue),
            "most_overdue_days": (today - worst.due_date).days,
            "most_overdue_title": worst.title,
        }

    def _task_overdue_condition(self, values: dict) -> bool:
        return values["overdue_task_count"] > 0

    def _check_task_overdue(self, business_id: UUID) -> OpportunityFinding | None:
        values = self._current_task_overdue_values(business_id)
        if not self._task_overdue_condition(values):
            return None
        count = values["overdue_task_count"]
        days_overdue = values["most_overdue_days"]
        title = (
            f"'{values['most_overdue_title']}' is {days_overdue} days overdue"
            if count == 1
            else f"{count} tasks are more than {TASK_OVERDUE_DAYS_THRESHOLD} days overdue"
        )
        severity = (
            OpportunityFindingSeverity.HIGH
            if days_overdue > TASK_OVERDUE_HIGH_SEVERITY_DAYS
            else OpportunityFindingSeverity.MEDIUM
        )
        return self._create_if_new(business_id, OpportunityFindingType.TASK_OVERDUE, severity, title, values)

    def _resolution_note_task_overdue(self, before: dict, after: dict) -> str:
        return (
            f"No tasks are more than {TASK_OVERDUE_DAYS_THRESHOLD} days overdue anymore "
            f"(the most overdue task was {before['most_overdue_days']} days late when this was flagged)."
        )

    def _current_website_values(self, business_id: UUID) -> dict:
        brief = (
            self.db.query(WebsiteBrief)
            .filter(WebsiteBrief.business_id == business_id)
            .order_by(WebsiteBrief.created_at.desc())
            .first()
        )
        if not brief:
            return {"website_brief_id": None, "website_brief_title": None, "site_url": None}
        return {"website_brief_id": str(brief.id), "website_brief_title": brief.title, "site_url": brief.site_url}

    def _website_not_connected_condition(self, values: dict) -> bool:
        return values["website_brief_id"] is not None and not values["site_url"]

    def _check_website_not_connected(self, business_id: UUID) -> OpportunityFinding | None:
        values = self._current_website_values(business_id)
        if not self._website_not_connected_condition(values):
            return None
        title = "Website brief generated, but no live site connected yet"
        return self._create_if_new(
            business_id, OpportunityFindingType.WEBSITE_NOT_CONNECTED, OpportunityFindingSeverity.LOW, title, values
        )

    def _resolution_note_website(self, before: dict, after: dict) -> str:
        return f"A live site URL ({after['site_url']}) has since been added to the website brief."

    def _current_stripe_sync_values(self, business_id: UUID) -> dict:
        connection = (
            self.db.query(StripeConnection).filter(StripeConnection.business_id == business_id).first()
        )
        if not connection:
            return {"connected": False, "hours_since_last_sync": None, "last_synced_at": None}

        latest_synced = (
            self.db.query(RevenueEntry)
            .filter(RevenueEntry.business_id == business_id, RevenueEntry.origin == RevenueEntryOrigin.STRIPE)
            .order_by(RevenueEntry.created_at.desc())
            .first()
        )
        reference_time = latest_synced.created_at if latest_synced else connection.connected_at
        age_hours = (datetime.now(timezone.utc) - reference_time).total_seconds() / 3600
        return {"connected": True, "hours_since_last_sync": round(age_hours, 1), "last_synced_at": reference_time.isoformat()}

    def _stripe_sync_stale_condition(self, values: dict) -> bool:
        return (
            values["connected"]
            and values["hours_since_last_sync"] is not None
            and values["hours_since_last_sync"] >= STRIPE_SYNC_STALE_HOURS
        )

    def _check_stripe_sync_stale(self, business_id: UUID) -> OpportunityFinding | None:
        values = self._current_stripe_sync_values(business_id)
        if not self._stripe_sync_stale_condition(values):
            return None
        title = f"Stripe hasn't synced new revenue in {int(values['hours_since_last_sync'])} hours"
        return self._create_if_new(
            business_id, OpportunityFindingType.STRIPE_SYNC_STALE, OpportunityFindingSeverity.MEDIUM, title, values
        )

    def _resolution_note_stripe_sync(self, before: dict, after: dict) -> str:
        if not after["connected"]:
            # Disconnecting isn't "fixing" staleness, but it does make
            # the condition this check measures no longer true - report
            # that honestly rather than staying silent about it.
            return "Stripe was disconnected, so this sync-staleness check no longer applies."
        return (
            f"Stripe synced new revenue {after['hours_since_last_sync']:.1f} hours ago "
            f"(was stale for {before['hours_since_last_sync']:.1f} hours when this was flagged)."
        )

    async def check_website_content_changed(self, business_id: UUID) -> OpportunityFinding | None:
        """
        Re-scrapes the business's live site (the latest WebsiteBrief with
        a site_url set, same "latest brief" convention
        _current_website_values already uses) and compares against the
        hash from the last scrape.

        Deliberately NOT one of the five threshold checks above: it needs
        a real async network call (the others are pure DB queries), and
        it has a required side effect - the new hash/timestamp/word count
        are stored whether or not a finding is created, so the next
        comparison is always against the freshest content. That's also
        why it isn't in _evaluators/_resolution_notes: content changing
        is a one-time event, not a state to re-evaluate later (see the
        skip in check_resolutions above).

        The very first scrape for a brief has nothing to compare against
        - previous_hash is None, so this only establishes the baseline
        and never creates a finding on that run.
        """
        # Same "latest brief overall, then check its site_url" query
        # _current_website_values already uses - not filtering on site_url
        # in the WHERE clause, so both checks always agree on which brief
        # is "current" (a regenerated brief with no site_url is
        # consistently "not connected" for both checks, never a stale
        # older brief silently re-scraped instead).
        brief = (
            self.db.query(WebsiteBrief)
            .filter(WebsiteBrief.business_id == business_id)
            .order_by(WebsiteBrief.created_at.desc())
            .first()
        )
        if not brief or not brief.site_url:
            return None

        try:
            raw_text = await self.scraper.scrape(brief.site_url)
        except WebsiteUnreachableError:
            # A temporarily-down or now-blocking site must never corrupt
            # the stored comparison baseline - leave it untouched and try
            # again next scheduled run, same "don't work around a real
            # failure" discipline the scraper itself already documents.
            logger.warning("Opportunity Radar re-scrape failed for business %s", business_id)
            return None

        new_word_count = len(raw_text.split())
        new_hash = _hash_content(_normalize_for_hash(raw_text))
        previous_hash = brief.last_scraped_content_hash
        previous_word_count = brief.last_scraped_word_count

        finding = None
        if previous_hash and previous_hash != new_hash:
            title = self._website_content_changed_title(previous_word_count, new_word_count)
            finding = self._create_if_new(
                business_id,
                OpportunityFindingType.WEBSITE_CONTENT_CHANGED,
                OpportunityFindingSeverity.LOW,
                title,
                {
                    "site_url": brief.site_url,
                    "previous_word_count": previous_word_count,
                    "new_word_count": new_word_count,
                },
            )

        brief.last_scraped_content_hash = new_hash
        brief.last_scraped_at = datetime.now(timezone.utc)
        brief.last_scraped_word_count = new_word_count
        self.db.add(brief)
        self.db.commit()

        return finding

    def _website_content_changed_title(self, previous_word_count: int | None, new_word_count: int) -> str:
        # Word count is the one honest, cheaply-verifiable "what changed"
        # signal available without storing/diffing full page text (see
        # the hash-only design above) - it can't say WHAT changed, only
        # roughly how much. When the count happens to be identical despite
        # the hash differing (words swapped for others of the same total
        # count), fall back to the fully generic, still-honest phrasing
        # rather than reporting a misleading "no change" word count.
        if previous_word_count is not None and new_word_count != previous_word_count:
            direction = "up" if new_word_count > previous_word_count else "down"
            return (
                f"Website content has changed since it was last checked "
                f"(word count {direction} from {previous_word_count} to {new_word_count})"
            )
        return "Website content has changed since it was last checked"

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
