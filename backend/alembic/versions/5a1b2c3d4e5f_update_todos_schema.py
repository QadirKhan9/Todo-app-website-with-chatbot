"""Update todos table schema to match model

Revision ID: 5a1b2c3d4e5f
Revises: 26e6c0975131
Create Date: 2026-02-01 01:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '5a1b2c3d4e5f'
down_revision: Union[str, Sequence[str], None] = '26e6c0975131'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check if columns already exist
    connection = op.get_bind()
    result = connection.execute(sa.text("PRAGMA table_info(todos)")).fetchall()
    column_names = [row[1] for row in result]

    # Add the status column as an enum type (SQLite doesn't support ENUM, so we'll use VARCHAR)
    if 'status' not in column_names:
        op.add_column('todos', sa.Column('status', sa.String(20), nullable=True))

    # Add the priority column as an enum type (SQLite doesn't support ENUM, so we'll use VARCHAR)
    if 'priority' not in column_names:
        op.add_column('todos', sa.Column('priority', sa.String(20), nullable=True))

    # Add the completed_at column
    if 'completed_at' not in column_names:
        op.add_column('todos', sa.Column('completed_at', sa.DateTime(), nullable=True))

    # Update existing records to set status based on is_completed if the column still exists
    # Note: is_completed is a boolean field that might exist in the current schema
    connection = op.get_bind()
    if 'is_completed' in column_names:
        connection.execute(sa.text("""
            UPDATE todos
            SET status = CASE
                WHEN is_completed THEN 'COMPLETED'
                ELSE 'PENDING'
            END
            WHERE status IS NULL
        """))

        # Drop the old is_completed column if it exists
        op.drop_column('todos', 'is_completed')

    # Set default values for priority and status
    connection.execute(sa.text("UPDATE todos SET priority = 'MEDIUM' WHERE priority IS NULL"))
    connection.execute(sa.text("UPDATE todos SET status = 'PENDING' WHERE status IS NULL"))

    # SQLite doesn't support ALTER COLUMN, so we'll keep them nullable
    # The application logic should enforce that these columns are not null


def downgrade() -> None:
    """Downgrade schema."""
    # Add back the is_completed column
    op.add_column('todos', sa.Column('is_completed', sa.Boolean(), nullable=True))
    
    # Update records to set is_completed based on status
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE todos 
        SET is_completed = CASE 
            WHEN status = 'COMPLETED' THEN TRUE 
            ELSE FALSE 
        END
    """))
    
    # Make is_completed non-nullable
    op.alter_column('todos', 'is_completed', nullable=False)
    
    # Drop the new columns
    op.drop_column('todos', 'completed_at')
    op.drop_column('todos', 'priority')
    op.drop_column('todos', 'status')
    
    # Drop enums
    status_enum = postgresql.ENUM(name='todostatus')
    status_enum.drop(op.get_bind(), checkfirst=True)
    
    priority_enum = postgresql.ENUM(name='todopriority')
    priority_enum.drop(op.get_bind(), checkfirst=True)