from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies.auth_dependencies import require_active_business
from app.dependencies.db_dependencies import get_db
from app.models.business import Business
from app.models.task import TaskStatus
from app.schemas.common import Envelope, ResponseMeta
from app.schemas.task import TaskCreateRequest, TaskOut, TaskUpdateRequest
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _envelope(data):
    return Envelope(data=data, meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))


@router.get("", response_model=Envelope[list[TaskOut]])
def list_tasks(
    status: TaskStatus | None = Query(default=None),
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    tasks = TaskService(db).list(business.id, status)
    return _envelope([TaskOut.model_validate(t) for t in tasks])


@router.post("", response_model=Envelope[TaskOut])
def create_task(
    payload: TaskCreateRequest,
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    task = TaskService(db).create(business.id, payload)
    return _envelope(TaskOut.model_validate(task))


@router.patch("/{task_id}", response_model=Envelope[TaskOut])
def update_task(
    task_id: UUID,
    payload: TaskUpdateRequest,
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    task = TaskService(db).update(task_id, business.id, payload)
    return _envelope(TaskOut.model_validate(task))


@router.post("/{task_id}/complete", response_model=Envelope[TaskOut])
def complete_task(
    task_id: UUID,
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    task = TaskService(db).complete(task_id, business.id)
    return _envelope(TaskOut.model_validate(task))


@router.delete("/{task_id}")
def delete_task(
    task_id: UUID,
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    TaskService(db).delete(task_id, business.id)
    return _envelope({"deleted": True})
