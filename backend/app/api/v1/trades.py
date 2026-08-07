from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.auth_dependencies import require_active_business
from app.dependencies.db_dependencies import get_db
from app.models.business import Business
from app.schemas.common import Envelope, ResponseMeta
from app.schemas.trade import PortfolioSummaryOut, TradeCreateRequest, TradeOut
from app.services.trade_service import TradeService

router = APIRouter(prefix="/trades", tags=["trades"])


def _envelope(data):
    return Envelope(data=data, meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))


@router.get("", response_model=Envelope[list[TradeOut]])
def list_trades(business: Business = Depends(require_active_business), db: Session = Depends(get_db)):
    trades = TradeService(db).list_trades(business.id)
    return _envelope([TradeOut.model_validate(t) for t in trades])


@router.post("", response_model=Envelope[TradeOut])
def create_trade(
    payload: TradeCreateRequest,
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    trade = TradeService(db).create(business.id, payload)
    return _envelope(TradeOut.model_validate(trade))


@router.delete("/{trade_id}")
def delete_trade(
    trade_id: UUID,
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    TradeService(db).delete(trade_id, business.id)
    return _envelope({"deleted": True})


@router.get("/portfolio", response_model=Envelope[PortfolioSummaryOut])
def portfolio_summary(business: Business = Depends(require_active_business), db: Session = Depends(get_db)):
    summary = TradeService(db).get_portfolio_summary(business.id)
    return _envelope(summary)