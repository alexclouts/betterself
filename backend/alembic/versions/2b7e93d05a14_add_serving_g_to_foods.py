"""add serving_g to foods

Revision ID: 2b7e93d05a14
Revises: 8d41f6a2c9e7
Create Date: 2026-11-21 23:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b7e93d05a14'
down_revision: Union[str, Sequence[str], None] = '8d41f6a2c9e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'foods',
        sa.Column('serving_g', sa.Numeric(precision=8, scale=2), nullable=True),
    )
    op.create_check_constraint(
        'foods_check_serving',
        'foods',
        'serving_g IS NULL OR serving_g > 0',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('foods_check_serving', 'foods', type_='check')
    op.drop_column('foods', 'serving_g')
