import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPrimaryKeyMixin


class OpportunityFindingType(str, enum.Enum):
    REVENUE_DROP = "revenue_drop"
    REVENUE_STREAK = "revenue_streak"
    TASK_OVERDUE = "task_overdue"
    WEBSITE_NOT_CONNECTED = "website_not_connected"
    STRIPE_SYNC_STALE = "stripe_sync_stale"
    WEBSITE_CONTENT_CHANGED = "website_content_changed"


class OpportunityFindingSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class OpportunityFinding(Base, UUIDPrimaryKeyMixin):
    """
    LuminOS's first PROACTIVE feature - every other AI feature (CEO
    Briefing, Health Score, the Assistant) is reactive, generated only
    on request. These rows are created by a scheduled background job
    (see core/scheduler.py) without anyone asking.

    Deliberately rule-based only: `title` is plain string formatting
    with real computed numbers, never an AI call, and `details` holds
    the actual numbers behind the finding so it's always inspectable
    and re-derivable - same "code computes" discipline Health Score's
    numeric scores already follow. `resolution_note` follows the same
    discipline for resolved findings - see
    OpportunityRadarService.check_resolutions.
    """

    __tablename__ = "opportunity_findings"

    business_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), index=True
    )
    finding_type: Mapped[OpportunityFindingType] = mapped_column(
        Enum(OpportunityFindingType, name="opportunity_finding_type")
    )
    severity: Mapped[OpportunityFindingSeverity] = mapped_column(
        Enum(OpportunityFindingSeverity, name="opportunity_finding_severity")
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    details: Mapped[dict] = mapped_column(JSONB, default=dict)
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dismissed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    # Resolution tracking - independent of is_dismissed. Set only when a
    # scheduled re-check (see OpportunityRadarService.check_resolutions)
    # confirms the same threshold logic used to detect this finding no
    # longer holds. resolution_note is plain string formatting from real
    # before/after numbers, same as `title` - never an AI call.
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_note: Mapped[str | None] = mapped_column(String(300), nullable=True)
