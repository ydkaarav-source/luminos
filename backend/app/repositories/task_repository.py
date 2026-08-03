from uuid import UUID

from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_business(
        self, business_id: UUID, status: TaskStatus | None = None
    ) -> list[Task]:
        query = self.db.query(Task).filter(Task.business_id == business_id)
        if status:
            query = query.filter(Task.status == status)
        return query.order_by(Task.due_date.asc().nulls_last(), Task.created_at.desc()).all()

    def get(self, task_id: UUID) -> Task | None:
        return self.db.get(Task, task_id)

    def create(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def save(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()

    def count_completed_since(self, business_id: UUID, since) -> int:
        return (
            self.db.query(Task)
            .filter(
                Task.business_id == business_id,
                Task.status == TaskStatus.DONE,
                Task.completed_at >= since,
            )
            .count()
        )
