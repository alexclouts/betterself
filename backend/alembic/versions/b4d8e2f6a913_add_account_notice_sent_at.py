"""add account notice sent at

Revision ID: b4d8e2f6a913
Revises: 9f2a6c4e1d38
Create Date: 2026-11-28 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4d8e2f6a913'
down_revision: Union[str, Sequence[str], None] = '9f2a6c4e1d38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('account_notice_sent_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'account_notice_sent_at')
