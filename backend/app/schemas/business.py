from uuid import UUID

from pydantic import BaseModel

from app.models.business import BudgetRange, BusinessStage, BusinessType, PrimaryGoal


class BusinessOut(BaseModel):
    id: UUID
    name: str
    stage: BusinessStage
    business_type: BusinessType
    primary_goal: PrimaryGoal
    available_time_per_week: int | None
    budget_range: BudgetRange | None
    current_challenges: list[str] | None

    model_config = {"from_attributes": True}


class BusinessUpdateRequest(BaseModel):
    name: str | None = None
    stage: BusinessStage | None = None
    primary_goal: PrimaryGoal | None = None
