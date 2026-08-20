from datetime import date

from pydantic import BaseModel


class RevenuePoint(BaseModel):
    period: date
    amount: float


class TaskCompletionPoint(BaseModel):
    period: date
    completed: int
    created: int


class HealthScorePoint(BaseModel):
    calculated_at: date
    overall_score: int


class BusinessAnalyticsOut(BaseModel):
    revenue_over_time: list[RevenuePoint]
    task_completion_over_time: list[TaskCompletionPoint]
    health_score_history: list[HealthScorePoint]
    is_demo: bool = False