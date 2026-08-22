import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPrimaryKeyMixin


class ConversationRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationContext(str, enum.Enum):
    ASSISTANT_CHAT = "assistant_chat"
    BUSINESS_BUILDER = "business_builder"
    CEO_BRIEFING = "ceo_briefing"
    HEALTH_SCORE = "health_score"
    WEBSITE_BRIEF = "website_brief"


class AIConversation(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "ai_conversations"

    business_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    role: Mapped[ConversationRole] = mapped_column(Enum(ConversationRole, name="conversation_role"))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    context_type: Mapped[ConversationContext] = mapped_column(
        Enum(ConversationContext, name="conversation_context")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
