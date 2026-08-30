"""add_video_url_to_recordings

Revision ID: 521139d5f0c4
Revises: 90436800dbc5
Create Date: 2025-12-31 03:18:27.296551

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '521139d5f0c4'
down_revision: Union[str, Sequence[str], None] = '90436800dbc5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check if column already exists before adding
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('recordings')]
    
    if 'video_url' not in columns:
        op.add_column('recordings', sa.Column('video_url', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('recordings', 'video_url')
