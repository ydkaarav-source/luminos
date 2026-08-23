from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.revenue_entry import RevenueEntryOrigin


class RevenueEntryCreateRequest(BaseModel):
    amount: float = Field(gt=0)
    currency: str = "USD"
    source: str | None = None
    entry_date: date
    notes: str | None = None


class RevenueEntryOut(BaseModel):
    id: UUID
    amount: float
    currency: str
    source: str | None
    entry_date: date
    notes: str | None
    origin: RevenueEntryOrigin

    model_config = {"from_attributes": True}
