"""add units to foods

Revision ID: 5c3e8a1f7b24
Revises: 2b7e93d05a14
Create Date: 2026-11-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c3e8a1f7b24'
down_revision: Union[str, Sequence[str], None] = '2b7e93d05a14'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('foods', sa.Column('unit_name', sa.String(length=50), nullable=True))
    op.add_column('foods', sa.Column('unit_name_plural', sa.String(length=50), nullable=True))
    op.add_column('foods', sa.Column('unit_g', sa.Numeric(precision=8, scale=2), nullable=True))
    op.add_column(
        'foods',
        sa.Column('weight_is_estimated', sa.Boolean(), nullable=False, server_default='false'),
    )
    op.create_check_constraint(
        'foods_check_unit',
        'foods',
        '(unit_name IS NULL AND unit_name_plural IS NULL AND unit_g IS NULL) OR '
        '(unit_name IS NOT NULL AND unit_name_plural IS NOT NULL AND unit_g IS NOT NULL AND unit_g > 0)',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('foods_check_unit', 'foods', type_='check')
    op.drop_column('foods', 'weight_is_estimated')
    op.drop_column('foods', 'unit_g')
    op.drop_column('foods', 'unit_name_plural')
    op.drop_column('foods', 'unit_name')
