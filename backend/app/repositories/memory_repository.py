from datetime import datetime, timedelta, timezone
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

    def get_older_context(
        self,
        business_id: UUID,
        min_age_days: int = 14,
        memory_types: list[MemoryType] | None = None,
        limit: int = 5,
    ) -> list[MemoryRecord]:
        """
        A separate, deliberately OLDER slice of memory - for occasional
        "remembered that" callbacks (e.g. in CEO Briefing), not routine
        context. This is its own query, not a variant of `retrieve`: the
        two serve different purposes and must be free to diverge without
        risking each other's behavior.

        Defaults to DECISION and PREFERENCE - the "founder stated
        something meaningful" categories. FACT and onboarding-sourced
        records are routine background, not the kind of thing that makes
        a good callback.

        Ordered by relevance_score (the same signal `retrieve` already
        ranks by), not pure recency-among-old-records: recency here would
        only measure how long ago something crossed the age cutoff, which
        says nothing about whether it was actually significant.
        relevance_score is this app's only stored proxy for "was this
        meaningful when recorded" - a high-relevance memory from 40 days
        ago is a better callback candidate than a low-relevance one from
        15 days ago, so it's the more useful ordering here.
        """
        if memory_types is None:
            memory_types = [MemoryType.DECISION, MemoryType.PREFERENCE]
        cutoff = datetime.now(timezone.utc) - timedelta(days=min_age_days)
        return (
            self.db.query(MemoryRecord)
            .filter(
                MemoryRecord.business_id == business_id,
                MemoryRecord.memory_type.in_(memory_types),
                MemoryRecord.created_at <= cutoff,
            )
            .order_by(MemoryRecord.relevance_score.desc(), MemoryRecord.created_at.desc())
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
