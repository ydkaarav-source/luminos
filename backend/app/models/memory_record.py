import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPrimaryKeyMixin


class MemoryType(str, enum.Enum):
    FACT = "fact"
    DECISION = "decision"
    PREFERENCE = "preference"
    COMPLETED_MILESTONE = "completed_milestone"
    NOTE = "note"


class MemorySource(str, enum.Enum):
    ONBOARDING = "onboarding"
    ASSISTANT_CHAT = "assistant_chat"
    BUSINESS_BUILDER = "business_builder"
    WEBSITE_BRIEF = "website_brief"
    SCRAPED_SITE_CONTENT = "scraped_site_content"
    USER_MANUAL = "user_manual"
    SYSTEM_INFERRED = "system_inferred"


class MemoryRecord(Base, UUIDPrimaryKeyMixin):
    """
    The AI memory layer.

    Deliberately typed and discrete (not a raw transcript dump) so the
    AI orchestrator can retrieve a *relevant slice* of memory per call
    instead of stuffing an ever-growing chat log into every prompt.

    A vector `embedding` column can be added later (pgvector) for
    semantic retrieval - this design keeps that an additive migration.
    """

    __tablename__ = "memory_records"

    business_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), index=True
    )
    memory_type: Mapped[MemoryType] = mapped_column(Enum(MemoryType, name="memory_type"))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[MemorySource] = mapped_column(Enum(MemorySource, name="memory_source"))
    relevance_score: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
