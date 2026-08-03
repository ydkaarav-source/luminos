from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


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

    model_config = {"from_attributes": True}
