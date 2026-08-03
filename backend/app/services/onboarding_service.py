from sqlalchemy.orm import Session

from app.models.business import Business
from app.models.memory_record import MemorySource, MemoryType
from app.models.user import User
from app.repositories.business_repository import BusinessRepository
from app.repositories.memory_repository import MemoryRepository
from app.schemas.onboarding import BusinessStepRequest, ProfileStepRequest, ResourcesStepRequest


class OnboardingService:
    """
    Onboarding writes directly into `users` / `businesses`, and also
    seeds the memory layer with a few `preference`/`fact` records so the
    AI Assistant and Business Builder have real context from message one
    instead of starting cold.
    """

    def __init__(self, db: Session):
        self.db = db
        self.businesses = BusinessRepository(db)
        self.memory = MemoryRepository(db)

    def save_profile_step(self, user: User, payload: ProfileStepRequest) -> User:
        user.name = payload.name
        user.experience_level = payload.experience_level
        user.skills = payload.skills
        user.interests = payload.interests
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def save_business_step(self, user: User, payload: BusinessStepRequest) -> Business:
        business = Business(
            user_id=user.id,
            name=payload.business_name,
            stage=payload.stage,
            business_type=payload.business_type,
            primary_goal=payload.primary_goal,
        )
        business = self.businesses.create(business)

        self._seed_memory(
            business.id,
            f"Business stage at onboarding: {payload.stage.value}.",
            MemoryType.FACT,
        )
        self._seed_memory(
            business.id,
            f"Primary goal: {payload.primary_goal.value}.",
            MemoryType.PREFERENCE,
        )
        return business

    def save_resources_step(self, business: Business, payload: ResourcesStepRequest) -> Business:
        business.available_time_per_week = payload.available_time_per_week
        business.budget_range = payload.budget_range
        business.current_challenges = payload.current_challenges
        business = self.businesses.save(business)

        if payload.current_challenges:
            self._seed_memory(
                business.id,
                f"Founder-reported challenges: {', '.join(payload.current_challenges)}.",
                MemoryType.FACT,
            )
        return business

    def complete(self, user: User) -> User:
        user.onboarding_completed = True
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def _seed_memory(self, business_id, content: str, memory_type: MemoryType) -> None:
        from app.models.memory_record import MemoryRecord

        self.db.add(
            MemoryRecord(
                business_id=business_id,
                content=content,
                memory_type=memory_type,
                source=MemorySource.ONBOARDING,
            )
        )
        self.db.commit()
