import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
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

    `site_url`, once set, is periodically re-scraped by Opportunity
    Radar (see OpportunityRadarService.check_website_content_changed) to
    detect real content changes on the founder's live site -
    last_scraped_content_hash/_at/_word_count track that check's own
    state and are otherwise unused. Scoped to the specific brief row
    (not the business) deliberately: regenerating a brief - possibly
    with a different site_url - naturally starts a fresh comparison
    baseline rather than comparing against a URL that's no longer this
    brief's own.
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
    # SHA-256 hex digest (64 chars) of the normalized last-scraped page
    # text - not the raw text itself, so comparisons stay cheap and there's
    # no growing archive of a founder's scraped site content beyond what
    # memory_records already holds from the original one-shot scrape.
    last_scraped_content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_scraped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # A single number, not the text itself, kept alongside the hash so a
    # detected change can honestly report *how much* changed (word count
    # delta) without storing/diffing full page text.
    last_scraped_word_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
