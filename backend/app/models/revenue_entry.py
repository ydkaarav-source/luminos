import enum
import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class RevenueEntryOrigin(str, enum.Enum):
    MANUAL = "manual"
    STRIPE = "stripe"


class RevenueEntry(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "revenue_entries"

    business_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), index=True
    )
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    source: Mapped[str | None] = mapped_column(String(160), nullable=True)
    entry_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Distinguishes founder-entered revenue from revenue synced in from a
    # connected Stripe account - these must never be presented as the same
    # kind of entry. Existing rows predate this column and default to
    # MANUAL, which is accurate for all of them (Stripe sync is new).
    origin: Mapped[RevenueEntryOrigin] = mapped_column(
        Enum(RevenueEntryOrigin, name="revenue_entry_origin"),
        default=RevenueEntryOrigin.MANUAL,
        nullable=False,
    )
    # The Stripe charge id (ch_...) this entry was synced from, globally
    # unique - lets repeated syncs skip charges already imported. Null for
    # manually-entered rows.
    stripe_charge_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
