import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, SmallInteger, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPrimaryKeyMixin


class HealthScore(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "health_scores"

    business_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), index=True
    )
    overall_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    revenue_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    operations_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    marketing_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    customer_growth_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    financial_management_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    # {"strengths": [...], "weaknesses": [...], "recommendations": [...]}
    ai_explanation: Mapped[dict] = mapped_column(JSONB, default=dict)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
