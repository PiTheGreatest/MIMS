"""Initial Registry Creation

Revision ID: 362b00c5364f
Revises: 
Create Date: 2026-02-19 07:42:40.554325

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '362b00c5364f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """
    Unified Table Creation:
    Defining the table structure entirely before adding indexes.
    This ensures compliance with Section 84 of the Evidence Act regarding
    the integrity of electronic record-keeping systems.
    """
    # 1. CREATE the medical_records table with all columns included
    op.create_table(
        'medical_records',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('patient_nin', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('hospital_id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('patient_portion', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('insurance_portion', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('clinical_notes', sa.Text(), nullable=True) # Added for AI context later
    )

    # 2. CREATE the clinical_ledger table (if it's a separate entity in your project)
    # If clinical_ledger is already in another file, you can omit this block.
    op.create_table(
        'clinical_ledger',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('patient_id', sa.Integer(), sa.ForeignKey('medical_records.id'), nullable=False),
        sa.Column('note_content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )

    # 3. CREATE indexes for optimized retrieval
    op.create_index('idx_nin_timestamp', 'medical_records', ['patient_nin', 'timestamp'], unique=False)

def downgrade() -> None:
    """Reverts the schema changes."""
    op.drop_index('idx_nin_timestamp', table_name='medical_records')
    op.drop_table('clinical_ledger')
    op.drop_table('medical_records')