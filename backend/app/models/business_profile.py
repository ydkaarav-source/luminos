"""
Narrative business context, kept in its own table from `businesses`.

`businesses` holds short operational fields (stage, type, budget, etc.)
that get queried constantly across the app - task lists, dashboards,
health score. This table holds longer narrative text (industry, a real
description, products/services, target customers, goals) that AI
features read but the rest of the app doesn't - keeping it separate
means those frequent operational queries never have to scan past wide
text columns they don't need.

Strictly 1-to-1 with `businesses`: the unique constraint on
`business_id` enforces at most one profile per business at the
database level, not just in application code.
"""
import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class BusinessProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "business_profiles"

    business_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    industry: Mapped[str | None] = mapped_column(String(120), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    products_services: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_customers: Mapped[str | None] = mapped_column(Text, nullable=True)
    company_goals: Mapped[str | None] = mapped_column(Text, nullable=True)
