from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.memory_record import MemorySource, MemoryType


class MemoryRecordOut(BaseModel):
    id: UUID
    memory_type: MemoryType
    content: str
    source: MemorySource
    relevance_score: float
    created_at: datetime

    model_config = {"from_attributes": True}


class MemoryRecordUpdateRequest(BaseModel):
    content: str
