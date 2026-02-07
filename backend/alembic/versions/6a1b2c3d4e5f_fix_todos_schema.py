"""Fix todos table schema to match model

Revision ID: 6a1b2c3d4e5f
Revises: 5a1b2c3d4e5f
Create Date: 2026-02-01 01:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '6a1b2c3d4e5f'
down_revision: Union[str, Sequence[str], None] = '5a1b2c3d4e5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check if status column exists, if not create it
    conn = op.get_bind()

    # Check if the status column exists (using SQLite syntax)
    result = conn.execute(sa.text("PRAGMA table_info(todos)")).fetchall()
    column_names = [row[1] for row in result]

    if 'status' not in column_names:
        # Add the status column (SQLite doesn't support ENUM, so we'll use VARCHAR)
        op.add_column('todos', sa.Column('status', sa.String(20), nullable=True))

        # Update existing records to set status based on is_completed (if the column still exists)
        # Check if is_completed column exists first
        if 'is_completed' in column_names:
            conn.execute(sa.text("""
                UPDATE todos
                SET status = CASE
                    WHEN is_completed THEN 'COMPLETED'
                    ELSE 'PENDING'
                END
            """))

            # Drop the old is_completed column
            op.drop_column('todos', 'is_completed')
        else:
            # If is_completed doesn't exist, set default status
            conn.execute(sa.text("UPDATE todos SET status = 'PENDING' WHERE status IS NULL"))

        # Set default status for any remaining NULL values
        conn.execute(sa.text("UPDATE todos SET status = 'PENDING' WHERE status IS NULL"))

        # SQLite doesn't support ALTER COLUMN, so we'll keep it nullable
        # The application logic should enforce that this column is not null

    # Check if priority column exists
    if 'priority' not in column_names:
        # Add the priority column (SQLite doesn't support ENUM, so we'll use VARCHAR)
        op.add_column('todos', sa.Column('priority', sa.String(20), nullable=True))

        # Set default priority
        conn.execute(sa.text("UPDATE todos SET priority = 'MEDIUM' WHERE priority IS NULL"))

        # SQLite doesn't support ALTER COLUMN, so we'll keep it nullable
        # The application logic should enforce that this column is not null

    # Check if completed_at column exists
    if 'completed_at' not in column_names:
        # Add the completed_at column
        op.add_column('todos', sa.Column('completed_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Add back the is_completed column if it doesn't exist
    conn = op.get_bind()
    is_completed_exists = conn.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'todos' AND column_name = 'is_completed'
    """)).fetchone()
    
    if not is_completed_exists:
        op.add_column('todos', sa.Column('is_completed', sa.Boolean(), nullable=True))
        
        # Update records to set is_completed based on status
        conn.execute(sa.text("""
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