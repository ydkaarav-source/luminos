"""
One founder's OAuth connection to their OWN existing Stripe account.

LuminOS is a platform reading a connected Standard account's own
transaction history - never a marketplace, never holding funds, never
creating charges. `access_token` is the OAuth token Stripe returns,
which functions like a secret API key scoped to the connected account;
it must never be exposed to the frontend in any response. This app has
no existing encryption-at-rest pattern for sensitive columns (checked -
none exists), so per the same server-side-only discipline already used
for OPENAI_API_KEY, the guarantee here is schema/route-level: no schema
or route in this feature ever includes this column in a response.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class StripeConnection(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "stripe_connections"

    business_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    stripe_account_id: Mapped[str] = mapped_column(String(255), nullable=False)
    access_token: Mapped[str] = mapped_column(String(255), nullable=False)
    connected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
