"""add opportunity finding resolution tracking

Revision ID: c1f5a83b6e04
Revises: b8e3f61a7d92
Create Date: 2026-08-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c1f5a83b6e04'
down_revision: Union[str, None] = 'b8e3f61a7d92'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('opportunity_findings', sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('opportunity_findings', sa.Column('resolution_note', sa.String(length=300), nullable=True))


def downgrade() -> None:
    op.drop_column('opportunity_findings', 'resolution_note')
    op.drop_column('opportunity_findings', 'resolved_at')
