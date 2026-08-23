from datetime import datetime

from pydantic import BaseModel


class StripeConnectUrlOut(BaseModel):
    url: str


class StripeStatusOut(BaseModel):
    connected: bool
    connected_at: datetime | None
    stripe_account_id: str | None


class StripeSyncResultOut(BaseModel):
    synced_count: int
    total_fetched: int
