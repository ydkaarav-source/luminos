from datetime import datetime

from pydantic import BaseModel


class GoogleCalendarConnectUrlOut(BaseModel):
    url: str


class GoogleCalendarStatusOut(BaseModel):
    connected: bool
    connected_at: datetime | None
    google_email: str | None


class UpcomingEventOut(BaseModel):
    title: str
    start: str | None
    end: str | None
