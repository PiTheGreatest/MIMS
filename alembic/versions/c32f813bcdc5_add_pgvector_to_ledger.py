"""add_pgvector_to_ledger

Revision ID: c32f813bcdc5
Revises: 362b00c5364f
Create Date: 2026-04-16 03:35:55.389093

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = 'c32f813bcdc5'
down_revision: Union[str, Sequence[str], None] = '362b00c5364f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.add_column('clinical_ledger', sa.Column('embedding', Vector(1536), nullable=True))
    """Downgrade schema."""
    op.drop_column('clinical_ledger', 'embedding')
    op.execute("DROP EXTENSION IF EXISTS vector")
