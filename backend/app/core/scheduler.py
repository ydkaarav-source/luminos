"""
Automatic Stripe sync, running on an interval inside this app's own
process instead of requiring a manual "Sync now" click.

This app's Dockerfile runs uvicorn with no --workers flag - a single
worker process (confirmed when adding rate limiting, for the same
reason: in-memory/in-process state only works correctly with exactly
one worker). APScheduler's AsyncIOScheduler runs jobs on the same
asyncio event loop uvicorn already uses, so this needs no separate
process, message queue, or other new infrastructure - appropriate for
the current scale (syncing one connected account at a time, per
StripeService.sync_transactions's own design).

If this app is ever deployed with more than one worker, this needs to
move off an in-process scheduler - every worker would otherwise run its
own independent copy of this schedule, syncing each connected account
multiple times per interval instead of once. At that point, either a
single dedicated worker process (`--workers 1` isn't an option once
you need more capacity) or a Railway-triggered endpoint hit by an
external cron service (e.g. cron-job.org, or Railway's own Cron Jobs
against a one-off "sync" service) would be the right fix.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.logging import get_logger
from app.db.session import SessionLocal
from app.models.stripe_connection import StripeConnection
from app.services.stripe_service import StripeService

logger = get_logger(__name__)

SYNC_INTERVAL_HOURS = 4

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


def start_scheduler() -> None:
    scheduler.add_job(
        sync_all_connected_accounts,
        trigger="interval",
        hours=SYNC_INTERVAL_HOURS,
        id="stripe_sync_all",
        replace_existing=True,
    )
    scheduler.start()
