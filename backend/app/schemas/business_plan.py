from uuid import UUID

from pydantic import BaseModel

from app.models.business_plan import BusinessPlanStatus


class BusinessBuilderGenerateRequest(BaseModel):
    idea_description: str


class BusinessOverview(BaseModel):
    target_customer: str
    problem_solved: str
    revenue_model: str
    competition: str
    risks: str


class RoadmapMonth(BaseModel):
    month: int
    focus: str
    milestones: list[str]


class ActionPlan(BaseModel):
    daily_tasks: list[str]
    weekly_goals: list[str]
    milestones: list[str]


class BusinessPlanOut(BaseModel):
    id: UUID
    title: str
    overview: BusinessOverview
    roadmap: list[RoadmapMonth]
    action_plan: ActionPlan
    status: BusinessPlanStatus

    model_config = {"from_attributes": True}
