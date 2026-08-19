import json
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from app.models.ai_conversation import ConversationRole
from app.models.ai_insight import AIInsight


class AssistantMessageRequest(BaseModel):
    content: str


class AssistantMessageOut(BaseModel):
    role: ConversationRole
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CEOBriefingOut(BaseModel):
    id: UUID
    finding: str
    why: list[str]
    recommendation: str
    confidence: Literal["high", "medium", "low"]
    is_read: bool
    generated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_insight(cls, insight: AIInsight) -> "CEOBriefingOut":
        """
        AIInsight stores this feature's structured content in its existing
        title/body/priority columns rather than a dedicated table - see
        ceo_briefing_service.py for how those get written. Briefings
        generated before this change have a plain-text body from the old
        prompt shape, not JSON; those are read back as a best-effort
        legacy view instead of raising, so existing history doesn't break
        for already-live users.
        """
        try:
            payload = json.loads(insight.body)
            why = payload["why"]
            recommendation = payload["recommendation"]
        except (json.JSONDecodeError, KeyError, TypeError):
            why = []
            recommendation = insight.body

        return cls(
            id=insight.id,
            finding=insight.title,
            why=why,
            recommendation=recommendation,
            confidence=insight.priority.value,
            is_read=insight.is_read,
            generated_at=insight.generated_at,
        )
