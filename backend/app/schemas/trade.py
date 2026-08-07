from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.trade import TradeSide


class TradeCreateRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=20)
    side: TradeSide
    quantity: float = Field(gt=0)
    price: float = Field(gt=0)
    trade_date: date
    notes: str | None = None


class TradeOut(BaseModel):
    id: UUID
    symbol: str
    side: TradeSide
    quantity: float
    price: float
    trade_date: date
    notes: str | None

    model_config = {"from_attributes": True}


class PositionOut(BaseModel):
    symbol: str
    quantity: float
    average_cost: float
    total_cost: float
    realized_pl: float


class PortfolioSummaryOut(BaseModel):
    positions: list[PositionOut]
    total_realized_pl: float
    total_cost_basis: float