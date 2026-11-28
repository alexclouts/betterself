"""add email verification

Revision ID: 9f2a6c4e1d38
Revises: 5c3e8a1f7b24
Create Date: 2026-11-27 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f2a6c4e1d38'
down_revision: Union[str, Sequence[str], None] = '5c3e8a1f7b24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True),
    )
    # Les comptes créés avant cette migration sont considérés comme vérifiés :
    # sans cela, leurs propriétaires ne pourraient plus se connecter.
    op.execute("UPDATE users SET email_verified_at = now()")

    op.create_table(
        'email_verification_tokens',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash'),
    )
    op.create_index(
        op.f('ix_email_verification_tokens_user_id'),
        'email_verification_tokens',
        ['user_id'],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f('ix_email_verification_tokens_user_id'),
        table_name='email_verification_tokens',
    )
    op.drop_table('email_verification_tokens')
    op.drop_column('users', 'email_verified_at')
