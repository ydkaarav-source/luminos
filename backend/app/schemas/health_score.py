from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class HealthScoreExplanation(BaseModel):
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]


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

    model_config = {"from_attributes": True}
