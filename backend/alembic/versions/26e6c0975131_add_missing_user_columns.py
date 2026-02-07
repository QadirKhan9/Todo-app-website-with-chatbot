"""add missing user columns

Revision ID: 26e6c0975131
Revises: 445833dbd4fd
Create Date: 2026-01-22 23:22:50.213642

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '26e6c0975131'
down_revision: Union[str, Sequence[str], None] = '445833dbd4fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check which columns already exist
    connection = op.get_bind()
    result = connection.execute(sa.text("PRAGMA table_info(users)")).fetchall()
    column_names = [row[1] for row in result]

    # Add missing columns to users table as nullable initially
    if 'hashed_password' not in column_names:
        op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=True))
    if 'is_active' not in column_names:
        op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True, default=True))
    if 'email_verified' not in column_names:
        op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=True, default=False))

    # Update existing records with default values
    connection = op.get_bind()
    connection.execute(sa.text("UPDATE users SET is_active = 1 WHERE is_active IS NULL"))
    connection.execute(sa.text("UPDATE users SET email_verified = 0 WHERE email_verified IS NULL"))

    # SQLite doesn't support ALTER COLUMN, so we'll keep them nullable
    # The application logic should enforce that these columns are not null


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the added columns
    op.drop_column('users', 'email_verified')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'hashed_password')
