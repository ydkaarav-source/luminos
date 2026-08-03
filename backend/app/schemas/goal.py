from datetime import date
from uuid import UUID

from pydantic import BaseModel

from app.models.goal import GoalStatus


class GoalCreateRequest(BaseModel):
    title: str
    description: str | None = None
    target_date: date | None = None


class GoalUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    target_date: date | None = None
    status: GoalStatus | None = None


class GoalOut(BaseModel):
    id: UUID
    title: str
    description: str | None
    target_date: date | None
    status: GoalStatus

    model_config = {"from_attributes": True}
