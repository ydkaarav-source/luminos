import csv
import io
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.revenue_entry import RevenueEntry
from app.models.task import Task


class ExportService:
    """
    Generates CSV exports of a business's own real data. Uses the
    standard library's csv module so quoting/escaping (commas,
    quotes, newlines inside a field) is handled correctly rather than
    hand-joining strings.
    """

    def __init__(self, db: Session):
        self.db = db

    def tasks_csv(self, business_id: UUID) -> str:
        tasks = (
            self.db.query(Task)
            .filter(Task.business_id == business_id)
            .order_by(Task.due_date.asc().nullslast())
            .all()
        )

        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            ["id", "title", "description", "status", "priority", "source", "due_date", "completed_at"]
        )
        for t in tasks:
            writer.writerow(
                [
                    t.id,
                    t.title,
                    t.description or "",
                    t.status.value,
                    t.priority.value,
                    t.source.value,
                    t.due_date.isoformat() if t.due_date else "",
                    t.completed_at.isoformat() if t.completed_at else "",
                ]
            )
        return buffer.getvalue()

    def revenue_csv(self, business_id: UUID) -> str:
        entries = (
            self.db.query(RevenueEntry)
            .filter(RevenueEntry.business_id == business_id)
            .order_by(RevenueEntry.entry_date.asc())
            .all()
        )

        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["id", "amount", "currency", "source", "origin", "entry_date", "notes"])
        for e in entries:
            writer.writerow(
                [
                    e.id,
                    e.amount,
                    e.currency,
                    e.source or "",
                    e.origin.value,
                    e.entry_date.isoformat(),
                    e.notes or "",
                ]
            )
        return buffer.getvalue()
