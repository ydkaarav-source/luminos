from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.task import Task, TaskStatus
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreateRequest, TaskUpdateRequest


class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.tasks = TaskRepository(db)

    def list(self, business_id: UUID, status: TaskStatus | None = None) -> list[Task]:
        return self.tasks.list_for_business(business_id, status)

    def create(self, business_id: UUID, payload: TaskCreateRequest) -> Task:
        task = Task(business_id=business_id, **payload.model_dump())
        return self.tasks.create(task)

    def update(self, task_id: UUID, business_id: UUID, payload: TaskUpdateRequest) -> Task:
        task = self._get_owned(task_id, business_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(task, field, value)
        if payload.status == TaskStatus.DONE and not task.completed_at:
            task.completed_at = datetime.now(timezone.utc)
        return self.tasks.save(task)

    def complete(self, task_id: UUID, business_id: UUID) -> Task:
        task = self._get_owned(task_id, business_id)
        task.status = TaskStatus.DONE
        task.completed_at = datetime.now(timezone.utc)
        return self.tasks.save(task)

    def delete(self, task_id: UUID, business_id: UUID) -> None:
        task = self._get_owned(task_id, business_id)
        self.tasks.delete(task)

    def _get_owned(self, task_id: UUID, business_id: UUID) -> Task:
        task = self.tasks.get(task_id)
        if not task or task.business_id != business_id:
            raise NotFoundError("Task not found.")
        return task
