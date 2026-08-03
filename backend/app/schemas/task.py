from datetime import date
from uuid import UUID

from pydantic import BaseModel

from app.models.task import TaskPriority, TaskSource, TaskStatus


class TaskCreateRequest(BaseModel):
    title: str
    description: str | None = None
    due_date: date | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    project_id: UUID | None = None
    goal_id: UUID | None = None


class TaskUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: date | None = None
    priority: TaskPriority | None = None
    status: TaskStatus | None = None


class TaskOut(BaseModel):
    id: UUID
    title: str
    description: str | None
    due_date: date | None
    priority: TaskPriority
    status: TaskStatus
    source: TaskSource
    project_id: UUID | None

    model_config = {"from_attributes": True}
