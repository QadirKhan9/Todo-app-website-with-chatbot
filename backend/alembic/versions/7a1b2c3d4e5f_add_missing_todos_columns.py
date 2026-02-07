"""Add missing todos columns

Revision ID: 7a1b2c3d4e5f
Revises: 6a1b2c3d4e5f
Create Date: 2026-02-01 01:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '7a1b2c3d4e5f'
down_revision: Union[str, Sequence[str], None] = '6a1b2c3d4e5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()

    # Check if due_date column exists (using SQLite syntax)
    result = conn.execute(sa.text("PRAGMA table_info(todos)")).fetchall()
    column_names = [row[1] for row in result]

    if 'due_date' not in column_names:
        # Add the due_date column with proper type
        op.add_column('todos', sa.Column('due_date', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the due_date column
    op.drop_column('todos', 'due_date')