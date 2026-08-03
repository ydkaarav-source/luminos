"""
Shared response envelope schemas used across every route.
"""
from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseMeta(BaseModel):
    generated_at: datetime


class Envelope(BaseModel, Generic[T]):
    data: T
    meta: ResponseMeta
