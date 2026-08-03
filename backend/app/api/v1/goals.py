from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.dependencies.auth_dependencies import require_active_business
from app.dependencies.db_dependencies import get_db
from app.models.business import Business
from app.models.goal import BusinessGoal
from app.schemas.common import Envelope, ResponseMeta
from app.schemas.goal import GoalCreateRequest, GoalOut, GoalUpdateRequest

router = APIRouter(prefix="/goals", tags=["goals"])


def _envelope(data):
    return Envelope(data=data, meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))


def _get_owned(db: Session, goal_id: UUID, business_id: UUID) -> BusinessGoal:
    goal = db.get(BusinessGoal, goal_id)
    if not goal or goal.business_id != business_id:
        raise NotFoundError("Goal not found.")
    return goal


@router.get("", response_model=Envelope[list[GoalOut]])
def list_goals(business: Business = Depends(require_active_business), db: Session = Depends(get_db)):
    goals = db.query(BusinessGoal).filter(BusinessGoal.business_id == business.id).all()
    return _envelope([GoalOut.model_validate(g) for g in goals])


@router.post("", response_model=Envelope[GoalOut])
def create_goal(
    payload: GoalCreateRequest,
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    goal = BusinessGoal(business_id=business.id, **payload.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return _envelope(GoalOut.model_validate(goal))


@router.patch("/{goal_id}", response_model=Envelope[GoalOut])
def update_goal(
    goal_id: UUID,
    payload: GoalUpdateRequest,
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    goal = _get_owned(db, goal_id, business.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return _envelope(GoalOut.model_validate(goal))


@router.delete("/{goal_id}")
def delete_goal(
    goal_id: UUID,
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    goal = _get_owned(db, goal_id, business.id)
    db.delete(goal)
    db.commit()
    return _envelope({"deleted": True})
