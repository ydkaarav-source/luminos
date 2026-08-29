"""add email_notifications_enabled to users

Revision ID: f6a1c8e30d75
Revises: e5f7b03d9a52
Create Date: 2026-08-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f6a1c8e30d75'
down_revision: Union[str, None] = 'e5f7b03d9a52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # server_default backfills existing rows to True (opt-out, matching
    # the model's own Python-side default for new rows going forward) -
    # same pattern as revenue_entries.origin in
    # e7f4c82a91d3_add_stripe_connections_and_revenue_origin.py.
    op.add_column(
        'users',
        sa.Column('email_notifications_enabled', sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade() -> None:
    op.drop_column('users', 'email_notifications_enabled')
