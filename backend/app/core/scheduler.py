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
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import or_

from app.core.logging import get_logger
from app.db.session import SessionLocal
from app.models.business import Business
from app.models.revenue_entry import RevenueEntry
from app.models.stripe_connection import StripeConnection
from app.models.task import Task
from app.models.user import User
from app.services.opportunity_radar_service import OpportunityRadarService
from app.services.stripe_service import StripeService

logger = get_logger(__name__)

SYNC_INTERVAL_HOURS = 4
# Opportunity Radar's signals (week-over-week revenue, days-overdue
# tasks, hours-since-last-Stripe-sync) are all day-granularity by
# nature - running this more than once a day wouldn't make any of them
# meaningfully fresher, and once daily keeps this appropriately light
# for what are explicitly "slower-moving" checks.
RADAR_INTERVAL_HOURS = 24

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
    completed onboarding AND at least one real revenue entry or task
    logged - a fresh, empty business has nothing to meaningfully check
    yet, and Demo Mode's fictional data is never persisted anywhere
    (see demo_data_service.py), so it can never appear here regardless -
    only genuinely real businesses with genuinely real data are ever
    checked, same discipline as everywhere else in this app.
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
                ),
            )
            .all()
        ]
    finally:
        db.close()

    for business_id in business_ids:
        db = SessionLocal()
        try:
            created = OpportunityRadarService(db).run_checks(business_id)
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
    scheduler.start()
