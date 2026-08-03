import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPrimaryKeyMixin


class InsightType(str, enum.Enum):
    CEO_BRIEFING = "ceo_briefing"
    PATTERN = "pattern"
    RECOMMENDATION = "recommendation"
    WARNING = "warning"


class InsightPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AIInsight(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "ai_insights"

    business_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), index=True
    )
    insight_type: Mapped[InsightType] = mapped_column(Enum(InsightType, name="insight_type"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[InsightPriority] = mapped_column(
        Enum(InsightPriority, name="insight_priority"), default=InsightPriority.MEDIUM
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
