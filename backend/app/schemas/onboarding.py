from pydantic import BaseModel, Field

from app.models.business import BudgetRange, BusinessType, PrimaryGoal, BusinessStage
from app.models.user import ExperienceLevel


class ProfileStepRequest(BaseModel):
    name: str
    experience_level: ExperienceLevel
    skills: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)


class BusinessStepRequest(BaseModel):
    business_name: str
    stage: BusinessStage
    business_type: BusinessType
    primary_goal: PrimaryGoal


class ResourcesStepRequest(BaseModel):
    available_time_per_week: int | None = None
    budget_range: BudgetRange | None = None
    current_challenges: list[str] = Field(default_factory=list)


class OnboardingStatusOut(BaseModel):
    onboarding_completed: bool
    has_business: bool
