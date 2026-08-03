import enum
import uuid
from typing import List, TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.goal import BusinessGoal
    from app.models.task import Task
    from app.models.project import Project


class BusinessStage(str, enum.Enum):
    IDEA = "idea"
    BUILDING = "building"
    OPERATING = "operating"
    GROWING = "growing"


class BusinessType(str, enum.Enum):
    ECOMMERCE = "ecommerce"
    SERVICE = "solopreneur_service"
    DIGITAL_PRODUCT = "digital_product"
    SAAS = "saas"
    OTHER = "other"


class PrimaryGoal(str, enum.Enum):
    START_FIRST_BUSINESS = "start_first_business"
    INCREASE_REVENUE = "increase_revenue"
    IMPROVE_ORGANIZATION = "improve_organization"
    SCALE_OPERATIONS = "scale_operations"


class BudgetRange(str, enum.Enum):
    UNDER_1K = "under_1k"
    ONE_TO_FIVE_K = "1k_5k"
    FIVE_TO_TWENTY_K = "5k_20k"
    TWENTY_K_PLUS = "20k_plus"


class Business(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "businesses"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    stage: Mapped[BusinessStage] = mapped_column(Enum(BusinessStage, name="business_stage"))
    business_type: Mapped[BusinessType] = mapped_column(Enum(BusinessType, name="business_type"))
    primary_goal: Mapped[PrimaryGoal] = mapped_column(Enum(PrimaryGoal, name="primary_goal"))
    available_time_per_week: Mapped[int | None] = mapped_column(Integer, nullable=True)
    budget_range: Mapped[BudgetRange | None] = mapped_column(
        Enum(BudgetRange, name="budget_range"), nullable=True
    )
    current_challenges: Mapped[List[str] | None] = mapped_column(ARRAY(String), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship(back_populates="businesses")
    goals: Mapped[List["BusinessGoal"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    tasks: Mapped[List["Task"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    projects: Mapped[List["Project"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
