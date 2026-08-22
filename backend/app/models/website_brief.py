import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class WebsiteBrief(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    An AI-generated website brief - suggested page structure, copy
    direction, and design direction for the founder to hand to a
    developer or website builder tool. Not a live site and not a
    guarantee of outcomes; see website_brief.py's prompt template.

    Not unique per business, same as BusinessPlan - a founder can
    regenerate as their business evolves, and GET /website-brief/latest
    reads the most recent row rather than upserting one.

    `site_url` is unused by this task - it exists now so a future task
    (fetching/scraping the founder's live site once built) can read
    from it without a second migration.
    """

    __tablename__ = "website_briefs"

    business_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    target_pages: Mapped[list] = mapped_column(JSONB, default=list)
    copy_direction: Mapped[str] = mapped_column(Text, nullable=False)
    design_direction: Mapped[str] = mapped_column(Text, nullable=False)
    site_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
