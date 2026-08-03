import enum
from typing import List

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ExperienceLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERIENCED = "experienced"


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    experience_level: Mapped[ExperienceLevel | None] = mapped_column(
        Enum(ExperienceLevel, name="experience_level"), nullable=True
    )
    # Postgres text[] - kept simple for MVP (no separate skills table)
    skills: Mapped[List[str] | None] = mapped_column(ARRAY(String), nullable=True)
    interests: Mapped[List[str] | None] = mapped_column(ARRAY(String), nullable=True)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    businesses: Mapped[List["Business"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
