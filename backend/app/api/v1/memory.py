from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.dependencies.auth_dependencies import require_active_business
from app.dependencies.db_dependencies import get_db
from app.models.business import Business
from app.repositories.memory_repository import MemoryRepository
from app.schemas.common import Envelope, ResponseMeta
from app.schemas.memory import MemoryRecordOut, MemoryRecordUpdateRequest

router = APIRouter(prefix="/memory", tags=["memory"])


def _envelope(data):
    return Envelope(data=data, meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))


@router.get("", response_model=Envelope[list[MemoryRecordOut]])
def list_memory(
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    records = MemoryRepository(db).list_for_business(business.id)
    return _envelope([MemoryRecordOut.model_validate(r) for r in records])


@router.patch("/{memory_id}", response_model=Envelope[MemoryRecordOut])
def update_memory(
    memory_id: UUID,
    payload: MemoryRecordUpdateRequest,
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    record = MemoryRepository(db).update(business.id, memory_id, payload.content)
    if not record:
        raise NotFoundError("Memory record not found.")
    return _envelope(MemoryRecordOut.model_validate(record))


@router.delete("/{memory_id}")
def delete_memory(
    memory_id: UUID,
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    deleted = MemoryRepository(db).delete(business.id, memory_id)
    if not deleted:
        raise NotFoundError("Memory record not found.")
    return _envelope({"deleted": True})
