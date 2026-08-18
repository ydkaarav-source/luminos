from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.business_profile import BusinessProfile


class BusinessProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_business_id(self, business_id: UUID) -> BusinessProfile | None:
        return (
            self.db.query(BusinessProfile)
            .filter(BusinessProfile.business_id == business_id)
            .first()
        )

    def upsert(self, business_id: UUID, data: dict) -> BusinessProfile:
        """
        Partial update if a row already exists for `business_id` (only the
        fields present in `data` are touched, everything else is left
        alone), otherwise creates one.

        The unique constraint on `business_id` is the actual safety net
        against a race between the SELECT and INSERT below - if two
        requests both find no existing row and both try to insert, the
        loser's commit raises IntegrityError, which we treat as "someone
        beat us to it" and fall back to an UPDATE instead of erroring.
        """
        existing = self.get_by_business_id(business_id)
        if existing:
            for field, value in data.items():
                setattr(existing, field, value)
            self.db.add(existing)
            self.db.commit()
            self.db.refresh(existing)
            return existing

        profile = BusinessProfile(business_id=business_id, **data)
        self.db.add(profile)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            existing = self.get_by_business_id(business_id)
            for field, value in data.items():
                setattr(existing, field, value)
            self.db.add(existing)
            self.db.commit()
            self.db.refresh(existing)
            return existing

        self.db.refresh(profile)
        return profile
