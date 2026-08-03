from uuid import UUID

from sqlalchemy.orm import Session

from app.models.business import Business


class BusinessRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active_for_user(self, user_id: UUID) -> Business | None:
        return (
            self.db.query(Business)
            .filter(Business.user_id == user_id, Business.is_active.is_(True))
            .order_by(Business.created_at.desc())
            .first()
        )

    def list_for_user(self, user_id: UUID) -> list[Business]:
        return self.db.query(Business).filter(Business.user_id == user_id).all()

    def create(self, business: Business) -> Business:
        self.db.add(business)
        self.db.commit()
        self.db.refresh(business)
        return business

    def save(self, business: Business) -> Business:
        self.db.add(business)
        self.db.commit()
        self.db.refresh(business)
        return business
