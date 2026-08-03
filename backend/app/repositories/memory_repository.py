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
