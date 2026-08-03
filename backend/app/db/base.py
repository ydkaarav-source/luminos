"""
Declarative base.

Deliberately import-light: every model file does `from app.db.base import
Base`, so this module must never import a model itself - doing so creates
a circular import the moment anything imports a model directly before
`app.db.base` has finished initializing. The "import every model so
Alembic can see them" concern lives in `app/db/model_registry.py`
instead, which is safe to import for side effects without being on the
hot path every model depends on.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass