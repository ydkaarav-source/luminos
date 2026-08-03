import enum
import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class BusinessPlanStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class BusinessPlan(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "business_plans"

    business_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    overview: Mapped[dict] = mapped_column(JSONB, default=dict)
    roadmap: Mapped[list] = mapped_column(JSONB, default=list)
    action_plan: Mapped[dict] = mapped_column(JSONB, default=dict)
    generated_by_ai: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[BusinessPlanStatus] = mapped_column(
        Enum(BusinessPlanStatus, name="business_plan_status"), default=BusinessPlanStatus.DRAFT
    )
