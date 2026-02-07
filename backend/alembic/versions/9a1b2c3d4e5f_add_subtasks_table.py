"""Add subtasks table for todo checklists

Revision ID: 9a1b2c3d4e5f
Revises: 8a1b2c3d4e5f
Create Date: 2026-02-03 03:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '9a1b2c3d4e5f'
down_revision: Union[str, Sequence[str], None] = '8a1b2c3d4e5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check if subtasks table already exists
    connection = op.get_bind()
    result = connection.execute(sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name='subtasks';")).fetchone()
    
    # Create the subtasks table only if it doesn't exist
    if result is None:
        op.create_table('subtasks',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('todo_id', sa.UUID(), nullable=False),
            sa.Column('title', sa.String(), nullable=False),
            sa.Column('is_completed', sa.Boolean(), nullable=False, default=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['todo_id'], ['todos.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_subtasks_todo_id'), 'subtasks', ['todo_id'])
        op.create_index(op.f('ix_subtasks_is_completed'), 'subtasks', ['is_completed'])
    else:
        print("Subtasks table already exists, skipping...")


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the subtasks table if it exists
    connection = op.get_bind()
    result = connection.execute(sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name='subtasks';")).fetchone()
    
    if result is not None:
        op.drop_table('subtasks')