"""
One founder's read-only OAuth connection to their OWN Google Calendar.

Unlike Stripe's Standard accounts (which only ever grant read_write
regardless of what's requested - confirmed the hard way in a prior
session), Google's OAuth genuinely honors a read-only scope grant:
this connection's refresh_token is only ever used to request
calendar.readonly-scoped access tokens - see google_calendar_service.py.

`refresh_token` is Google's long-lived token for renewing access
without re-authorization; it must never be exposed to the frontend in
any response, same server-side-only discipline already used for
Stripe's access_token (this app has no encryption-at-rest pattern for
sensitive columns - checked, none exists - so the guarantee here is
schema/route-level, not column-level encryption).

Upcoming events are deliberately never stored here or anywhere else -
they're fetched fresh from Google each time they're needed (see
get_upcoming_events), since calendar data changes frequently and a
persisted copy would just go stale.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class GoogleCalendarConnection(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "google_calendar_connections"

    business_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    # Sized larger than Stripe's access_token column (String(255)) since
    # Google refresh tokens don't have as tight a documented length bound -
    # a truncated security token is a worse failure than a few extra bytes.
    refresh_token: Mapped[str] = mapped_column(String(512), nullable=False)
    google_email: Mapped[str] = mapped_column(String(320), nullable=False)
    connected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
