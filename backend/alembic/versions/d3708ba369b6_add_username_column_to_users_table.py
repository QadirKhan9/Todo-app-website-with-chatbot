"""add username column to users table

Revision ID: d3708ba369b6
Revises:
Create Date: 2026-01-15 22:05:23.989445

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3708ba369b6'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check if username column already exists
    connection = op.get_bind()
    result = connection.execute(sa.text("PRAGMA table_info(users)")).fetchall()
    column_names = [row[1] for row in result]

    # Add username column to users table only if it doesn't exist
    if 'username' not in column_names:
        op.add_column('users', sa.Column('username', sa.String(length=50), nullable=True))
        # Create unique index for username
        op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

        # Update existing records with a default username based on email
        # This is a simplified approach - in production, you'd want to assign meaningful usernames
        connection = op.get_bind()
        # Use SQLite-compatible syntax
        connection.execute(sa.text("UPDATE users SET username = 'user_' || id WHERE username IS NULL"))
    else:
        print("Username column already exists, skipping...")

    # SQLite doesn't support ALTER COLUMN, so we'll keep it nullable
    # The application logic should enforce that username is not null


def downgrade() -> None:
    """Downgrade schema."""
    # Drop unique index for username
    op.drop_index(op.f('ix_users_username'), table_name='users')
    # Drop username column
    op.drop_column('users', 'username')