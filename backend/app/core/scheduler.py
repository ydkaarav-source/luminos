"""
Scheduled background jobs, running on an interval inside this app's own
process instead of requiring a manual trigger.

This app's Dockerfile runs uvicorn with no --workers flag - a single
worker process (confirmed when adding rate limiting, for the same
reason: in-memory/in-process state only works correctly with exactly
one worker). APScheduler's AsyncIOScheduler runs jobs on the same
asyncio event loop uvicorn already uses, so this needs no separate
process, message queue, or other new infrastructure.

If this app is ever deployed with more than one worker, this needs to
move off an in-process scheduler - every worker would otherwise run its
own independent copy of each schedule (syncing each connected Stripe
account multiple times per interval, or running Opportunity Radar
checks multiple times per business, instead of once). At that point,
either a single dedicated worker process (`--workers 1` isn't an
option once you need more capacity) or a Railway-triggered endpoint
hit by an external cron service (e.g. cron-job.org, or Railway's own
Cron Jobs against a one-off service) would be the right fix.
"""
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import or_

from app.core.logging import get_logger
from app.db.session import SessionLocal
from app.models.business import Business
from app.models.opportunity_finding import OpportunityFinding
from app.models.revenue_entry import RevenueEntry
from app.models.stripe_connection import StripeConnection
from app.models.task import Task
from app.models.user import User
from app.models.website_brief import WebsiteBrief
from app.services.opportunity_radar_service import MIN_RESOLUTION_CHECK_AGE_HOURS, OpportunityRadarService
from app.services.stripe_service import StripeService

logger = get_logger(__name__)

SYNC_INTERVAL_HOURS = 4
# Opportunity Radar's signals (week-over-week revenue, days-overdue
# tasks, hours-since-last-Stripe-sync) are all day-granularity by
# nature - running this more than once a day wouldn't make any of them
# meaningfully fresher, and once daily keeps this appropriately light
# for what are explicitly "slower-moving" checks.
RADAR_INTERVAL_HOURS = 24
# Same cadence as detection, and for the same reason - resolution
# signals are exactly as day-granular as detection signals (they reuse
# the identical threshold logic - see check_resolutions). Registered as
# its own job rather than tacked onto the end of
# run_opportunity_radar_all_businesses: the two operations select
# businesses differently (detection needs "onboarded + has real data",
# resolution-checking needs "has an eligible open finding"), and this
# app's existing scheduled jobs are each one concern, not several -
# keeping them separate also means a bug in resolution-checking can
# never block new detection from running, or vice versa.
RESOLUTION_CHECK_INTERVAL_HOURS = 24

scheduler = AsyncIOScheduler()


async def sync_all_connected_accounts() -> None:
    db = SessionLocal()
    try:
        business_ids = [row[0] for row in db.query(StripeConnection.business_id).all()]
    finally:
        db.close()

    for business_id in business_ids:
        db = SessionLocal()
        try:
            result = await StripeService(db).sync_transactions(business_id)
            logger.info("Scheduled Stripe sync for business %s: %s", business_id, result)
        except Exception:  # noqa: BLE001 - one broken connection must never stop the rest of the run
            logger.exception("Scheduled Stripe sync failed for business %s", business_id)
        finally:
            db.close()


async def run_opportunity_radar_all_businesses() -> None:
    """
    Runs Opportunity Radar checks for every business with a real,
    completed onboarding AND at least one real revenue entry, task, or
    connected live website logged - a fresh, empty business has nothing
    to meaningfully check yet, and Demo Mode's fictional data is never
    persisted anywhere (see demo_data_service.py), so it can never appear
    here regardless - only genuinely real businesses with genuinely real
    data are ever checked, same discipline as everywhere else in this
    app. The website-brief condition exists so a pre-revenue business
    that's only connected a live site still gets its content re-scraped.

    The website re-scrape check (check_website_content_changed) runs
    here too, in the same per-business loop, rather than as a separate
    scheduler.add_job() registration - it's still the same daily Radar
    sweep at the same interval, just with one check that needs a real
    network call instead of a DB query.
    """
    db = SessionLocal()
    try:
        business_ids = [
            row[0]
            for row in db.query(Business.id)
            .join(User, Business.user_id == User.id)
            .filter(
                User.onboarding_completed.is_(True),
                or_(
                    db.query(RevenueEntry.id).filter(RevenueEntry.business_id == Business.id).exists(),
                    db.query(Task.id).filter(Task.business_id == Business.id).exists(),
                    db.query(WebsiteBrief.id)
                    .filter(WebsiteBrief.business_id == Business.id, WebsiteBrief.site_url.isnot(None))
                    .exists(),
                ),
            )
            .all()
        ]
    finally:
        db.close()

    for business_id in business_ids:
        db = SessionLocal()
        try:
            radar = OpportunityRadarService(db)
            created = radar.run_checks(business_id)
            content_changed = await radar.check_website_content_changed(business_id)
            if content_changed:
                created.append(content_changed)
            if created:
                logger.info(
                    "Opportunity Radar created %d finding(s) for business %s",
                    len(created),
                    business_id,
                )
        except Exception:  # noqa: BLE001 - one broken business must never stop the rest of the run
            logger.exception("Opportunity Radar check failed for business %s", business_id)
        finally:
            db.close()


async def run_opportunity_radar_resolution_checks() -> None:
    """
    Re-checks every OPEN finding (resolved_at is null) that's old
    enough to meaningfully re-evaluate, across every business that
    actually has one - see OpportunityRadarService.check_resolutions
    for the per-finding logic. Scoping to businesses with an eligible
    open finding (rather than re-deriving the "onboarded + has real
    data" filter detection uses) is both simpler and more correct here:
    findings only ever exist for real businesses in the first place, so
    this query is naturally already restricted to them.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=MIN_RESOLUTION_CHECK_AGE_HOURS)
    db = SessionLocal()
    try:
        business_ids = [
            row[0]
            for row in db.query(OpportunityFinding.business_id)
            .filter(
                OpportunityFinding.resolved_at.is_(None),
                OpportunityFinding.detected_at <= cutoff,
            )
            .distinct()
            .all()
        ]
    finally:
        db.close()

    for business_id in business_ids:
        db = SessionLocal()
        try:
            resolved = OpportunityRadarService(db).check_resolutions(business_id)
            if resolved:
                logger.info(
                    "Opportunity Radar resolved %d finding(s) for business %s",
                    len(resolved),
                    business_id,
                )
        except Exception:  # noqa: BLE001 - one broken business must never stop the rest of the run
            logger.exception("Opportunity Radar resolution check failed for business %s", business_id)
        finally:
            db.close()


def start_scheduler() -> None:
    scheduler.add_job(
        sync_all_connected_accounts,
        trigger="interval",
        hours=SYNC_INTERVAL_HOURS,
        id="stripe_sync_all",
        replace_existing=True,
    )
    scheduler.add_job(
        run_opportunity_radar_all_businesses,
        trigger="interval",
        hours=RADAR_INTERVAL_HOURS,
        id="opportunity_radar_all",
        replace_existing=True,
    )
    scheduler.add_job(
        run_opportunity_radar_resolution_checks,
        trigger="interval",
        hours=RESOLUTION_CHECK_INTERVAL_HOURS,
        id="opportunity_radar_resolution_checks",
        replace_existing=True,
    )
    scheduler.start()
