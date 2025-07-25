"""add comment_date default

Revision ID: cf0b2e254a75
Revises: 9d4428da9f01
Create Date: 2025-07-18 15:04:32.672420

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf0b2e254a75'
down_revision: Union[str, Sequence[str], None] = '9d4428da9f01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        ALTER TABLE comments
        ALTER COLUMN comment_date
        TYPE TIMESTAMP WITH TIME ZONE
        USING comment_date::timestamptz
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        ALTER TABLE comments
        ALTER COLUMN comment_date
        TYPE VARCHAR
        USING comment_date::text
    """)
