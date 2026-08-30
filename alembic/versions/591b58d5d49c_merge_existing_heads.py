"""merge_existing_heads

Revision ID: 591b58d5d49c
Revises: 84a23e3b57d4, faa57ff9bf5a
Create Date: 2025-12-30 22:12:59.388101

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '591b58d5d49c'
down_revision: Union[str, Sequence[str], None] = ('84a23e3b57d4', 'faa57ff9bf5a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
