from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, RootModel


class RoleExplanation(BaseModel):
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]


class HealthScoreExplanation(RootModel[dict[str, RoleExplanation]]):
    """
    ai_explanation is now one RoleExplanation per executive role (cfo, cmo,
    coo, cro, ceo) instead of a single flat explanation - each role reasons
    over its own narrower slice of the score breakdown. Modeled as a dict
    rather than fixed role fields so this stays valid even if a role is
    added/removed without needing a schema change here.
    """

    root: dict[str, RoleExplanation]


class HealthScoreOut(BaseModel):
    id: UUID
    overall_score: int
    revenue_score: int
    operations_score: int
    marketing_score: int
    customer_growth_score: int
    financial_management_score: int
    ai_explanation: HealthScoreExplanation
    calculated_at: datetime
    is_demo: bool = False

    model_config = {"from_attributes": True}
