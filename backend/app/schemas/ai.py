from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.ai_conversation import ConversationRole
from app.models.ai_insight import InsightPriority, InsightType


class AssistantMessageRequest(BaseModel):
    content: str


class AssistantMessageOut(BaseModel):
    role: ConversationRole
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CEOBriefingOut(BaseModel):
    id: UUID
    title: str
    body: str
    priority: InsightPriority
    insight_type: InsightType
    is_read: bool
    generated_at: datetime

    model_config = {"from_attributes": True}
