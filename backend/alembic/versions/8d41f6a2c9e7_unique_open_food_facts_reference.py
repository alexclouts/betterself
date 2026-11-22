"""unique open food facts reference

Revision ID: 8d41f6a2c9e7
Revises: c07badeb4b97
Create Date: 2026-11-21 23:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d41f6a2c9e7'
down_revision: Union[str, Sequence[str], None] = 'c07badeb4b97'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        'uq_foods_open_food_facts_reference',
        'foods',
        ['external_reference_id'],
        unique=True,
        postgresql_where=sa.text("source = 'open_food_facts'"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('uq_foods_open_food_facts_reference', table_name='foods')
