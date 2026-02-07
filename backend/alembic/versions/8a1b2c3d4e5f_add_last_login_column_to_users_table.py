"""add last_login column to users table

Revision ID: 8a1b2c3d4e5f
Revises: 7a1b2c3d4e5f
Create Date: 2026-02-03 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a1b2c3d4e5f'
down_revision: Union[str, Sequence[str], None] = '7a1b2c3d4e5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check if last_login column already exists
    connection = op.get_bind()
    result = connection.execute(sa.text("PRAGMA table_info(users)")).fetchall()
    column_names = [row[1] for row in result]
    
    # Add last_login column to users table only if it doesn't exist
    if 'last_login' not in column_names:
        op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))
    else:
        print("last_login column already exists, skipping...")


def downgrade() -> None:
    """Downgrade schema."""
    # Drop last_login column if it exists
    connection = op.get_bind()
    result = connection.execute(sa.text("PRAGMA table_info(users)")).fetchall()
    column_names = [row[1] for row in result]
    
    if 'last_login' in column_names:
        op.drop_column('users', 'last_login')