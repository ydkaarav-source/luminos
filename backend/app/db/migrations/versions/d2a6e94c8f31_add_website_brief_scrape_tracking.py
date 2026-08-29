"""add website brief scrape tracking columns

Revision ID: d2a6e94c8f31
Revises: c1f5a83b6e04
Create Date: 2026-08-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd2a6e94c8f31'
down_revision: Union[str, None] = 'c1f5a83b6e04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('website_briefs', sa.Column('last_scraped_content_hash', sa.String(length=64), nullable=True))
    op.add_column('website_briefs', sa.Column('last_scraped_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('website_briefs', sa.Column('last_scraped_word_count', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('website_briefs', 'last_scraped_word_count')
    op.drop_column('website_briefs', 'last_scraped_at')
    op.drop_column('website_briefs', 'last_scraped_content_hash')
