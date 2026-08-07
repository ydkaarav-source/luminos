from collections import defaultdict
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.trade import Trade, TradeSide
from app.schemas.trade import PortfolioSummaryOut, PositionOut, TradeCreateRequest


class TradeService:
    def __init__(self, db: Session):
        self.db = db

    def list_trades(self, business_id: UUID) -> list[Trade]:
        return (
            self.db.query(Trade)
            .filter(Trade.business_id == business_id)
            .order_by(Trade.trade_date.desc(), Trade.created_at.desc())
            .all()
        )

    def create(self, business_id: UUID, payload: TradeCreateRequest) -> Trade:
        trade = Trade(business_id=business_id, **payload.model_dump())
        self.db.add(trade)
        self.db.commit()
        self.db.refresh(trade)
        return trade

    def delete(self, trade_id: UUID, business_id: UUID) -> None:
        trade = self.db.get(Trade, trade_id)
        if trade and trade.business_id == business_id:
            self.db.delete(trade)
            self.db.commit()

    def get_portfolio_summary(self, business_id: UUID) -> PortfolioSummaryOut:
        trades = (
            self.db.query(Trade)
            .filter(Trade.business_id == business_id)
            .order_by(Trade.trade_date.asc(), Trade.created_at.asc())
            .all()
        )

        state: dict[str, dict] = defaultdict(
            lambda: {"quantity": 0.0, "total_cost": 0.0, "realized_pl": 0.0}
        )

        for trade in trades:
            s = state[trade.symbol]
            qty = float(trade.quantity)
            price = float(trade.price)

            if trade.side == TradeSide.BUY:
                s["total_cost"] += qty * price
                s["quantity"] += qty
            else:
                if s["quantity"] > 0:
                    avg_cost = s["total_cost"] / s["quantity"]
                    sell_qty = min(qty, s["quantity"])
                    s["realized_pl"] += (price - avg_cost) * sell_qty
                    s["total_cost"] -= avg_cost * sell_qty
                    s["quantity"] -= sell_qty

        positions = [
            PositionOut(
                symbol=symbol,
                quantity=round(s["quantity"], 6),
                average_cost=round(s["total_cost"] / s["quantity"], 6) if s["quantity"] > 0 else 0.0,
                total_cost=round(s["total_cost"], 2),
                realized_pl=round(s["realized_pl"], 2),
            )
            for symbol, s in state.items()
            if s["quantity"] > 0 or s["realized_pl"] != 0
        ]

        return PortfolioSummaryOut(
            positions=positions,
            total_realized_pl=round(sum(p.realized_pl for p in positions), 2),
            total_cost_basis=round(sum(p.total_cost for p in positions), 2),
        )