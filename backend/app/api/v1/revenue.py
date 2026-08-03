from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies.auth_dependencies import require_active_business
from app.dependencies.db_dependencies import get_db
from app.models.business import Business
from app.models.revenue_entry import RevenueEntry
from app.schemas.common import Envelope, ResponseMeta
from app.schemas.revenue import RevenueEntryCreateRequest, RevenueEntryOut

router = APIRouter(prefix="/revenue", tags=["revenue"])


def _envelope(data):
    return Envelope(data=data, meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))


@router.get("", response_model=Envelope[list[RevenueEntryOut]])
def list_revenue(
    from_: date | None = Query(default=None, alias="from"),
    to: date | None = Query(default=None),
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    query = db.query(RevenueEntry).filter(RevenueEntry.business_id == business.id)
    if from_:
        query = query.filter(RevenueEntry.entry_date >= from_)
    if to:
        query = query.filter(RevenueEntry.entry_date <= to)
    entries = query.order_by(RevenueEntry.entry_date.desc()).all()
    return _envelope([RevenueEntryOut.model_validate(e) for e in entries])


@router.post("", response_model=Envelope[RevenueEntryOut])
def create_revenue(
    payload: RevenueEntryCreateRequest,
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    entry = RevenueEntry(business_id=business.id, **payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _envelope(RevenueEntryOut.model_validate(entry))


@router.delete("/{entry_id}")
def delete_revenue(entry_id, business: Business = Depends(require_active_business), db: Session = Depends(get_db)):
    entry = db.get(RevenueEntry, entry_id)
    if entry and entry.business_id == business.id:
        db.delete(entry)
        db.commit()
    return _envelope({"deleted": True})
