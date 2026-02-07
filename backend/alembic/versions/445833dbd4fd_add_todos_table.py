"""Add todos table

Revision ID: 445833dbd4fd
Revises: d3708ba369b6
Create Date: 2026-01-15 23:56:08.198274

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '445833dbd4fd'
down_revision: Union[str, Sequence[str], None] = 'd3708ba369b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check if todos table already exists
    connection = op.get_bind()
    result = connection.execute(sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name='todos';")).fetchone()

    # Create the todos table only if it doesn't exist
    if result is None:
        op.create_table('todos',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('user_id', sa.UUID(), nullable=False),
            sa.Column('title', sa.String(length=200), nullable=False),
            sa.Column('description', sa.String(length=1000), nullable=True),
            sa.Column('is_completed', sa.Boolean(), nullable=False),
            sa.Column('priority', sa.String(length=20), nullable=False),
            sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
    else:
        print("Todos table already exists, skipping...")


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the todos table
    op.drop_table('todos')