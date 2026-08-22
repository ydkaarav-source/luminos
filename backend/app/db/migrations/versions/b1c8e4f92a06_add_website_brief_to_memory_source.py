"""add website_brief to memory_source enum

Revision ID: b1c8e4f92a06
Revises: 9a2f6d1b3c47
Create Date: 2026-08-22 00:00:02.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'b1c8e4f92a06'
down_revision: Union[str, None] = '9a2f6d1b3c47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ALTER TYPE ... ADD VALUE cannot run inside the transaction Alembic
    # opens by default (Postgres requires it outside a transaction block),
    # so this commits the migration's transaction first.
    op.execute("COMMIT")
    op.execute("ALTER TYPE memory_source ADD VALUE IF NOT EXISTS 'WEBSITE_BRIEF'")


def downgrade() -> None:
    # Postgres has no ALTER TYPE ... DROP VALUE - removing an enum label
    # requires rebuilding the type, which isn't worth the risk here.
    pass
