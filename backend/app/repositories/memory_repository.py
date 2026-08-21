from uuid import UUID

from sqlalchemy.orm import Session

from app.models.memory_record import MemoryRecord, MemoryType


class MemoryRepository:
    """
    Retrieval for the MVP is recency + relevance ranked, scoped by
    memory type per calling context. Swapping to pgvector similarity
    search later only changes the query inside `retrieve`.
    """

    def __init__(self, db: Session):
        self.db = db

    def add(self, record: MemoryRecord) -> MemoryRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def retrieve(
        self,
        business_id: UUID,
        memory_types: list[MemoryType] | None = None,
        limit: int = 15,
    ) -> list[MemoryRecord]:
        query = self.db.query(MemoryRecord).filter(MemoryRecord.business_id == business_id)
        if memory_types:
            query = query.filter(MemoryRecord.memory_type.in_(memory_types))
        return (
            query.order_by(
                MemoryRecord.relevance_score.desc(), MemoryRecord.created_at.desc()
            )
            .limit(limit)
            .all()
        )

    def list_for_business(self, business_id: UUID) -> list[MemoryRecord]:
        return (
            self.db.query(MemoryRecord)
            .filter(MemoryRecord.business_id == business_id)
            .order_by(MemoryRecord.created_at.desc())
            .all()
        )

    def update(self, business_id: UUID, record_id: UUID, content: str) -> MemoryRecord | None:
        record = (
            self.db.query(MemoryRecord)
            .filter(MemoryRecord.id == record_id, MemoryRecord.business_id == business_id)
            .first()
        )
        if not record:
            return None
        record.content = content
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, business_id: UUID, record_id: UUID) -> bool:
        record = (
            self.db.query(MemoryRecord)
            .filter(MemoryRecord.id == record_id, MemoryRecord.business_id == business_id)
            .first()
        )
        if not record:
            return False
        self.db.delete(record)
        self.db.commit()
        return True
