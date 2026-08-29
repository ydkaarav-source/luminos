"""add website_content_changed to opportunity_finding_type enum

Revision ID: e5f7b03d9a52
Revises: d2a6e94c8f31
Create Date: 2026-08-28 00:00:01.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'e5f7b03d9a52'
down_revision: Union[str, None] = 'd2a6e94c8f31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ALTER TYPE ... ADD VALUE cannot run inside the transaction Alembic
    # opens by default (Postgres requires it outside a transaction block),
    # so this commits the migration's transaction first.
    op.execute("COMMIT")
    op.execute("ALTER TYPE opportunity_finding_type ADD VALUE IF NOT EXISTS 'WEBSITE_CONTENT_CHANGED'")


def downgrade() -> None:
    # Postgres has no ALTER TYPE ... DROP VALUE - removing an enum label
    # requires rebuilding the type, which isn't worth the risk here.
    pass
