"""initial

Revision ID: 5a155ea9a79d
Revises: 
Create Date: 2025-03-23 13:36:48.268494

"""
from typing import Sequence, Union

from alembic import op
import fastapi_users_db_sqlalchemy
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a155ea9a79d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('events',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('short_url', sa.String(), nullable=False),
    sa.Column('event_type', sa.Integer(), nullable=False),
    sa.Column('datetime', sa.DateTime(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_events_datetime'), 'events', ['datetime'], unique=False)
    op.create_index(op.f('ix_events_event_type'), 'events', ['event_type'], unique=False)
    op.create_index(op.f('ix_events_id'), 'events', ['id'], unique=False)
    op.create_index(op.f('ix_events_short_url'), 'events', ['short_url'], unique=False)
    op.create_table('short_url',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('short_name', sa.String(), nullable=False),
    sa.Column('original_url', sa.String(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=False),
    sa.Column('modify_time', sa.DateTime(), nullable=False),
    sa.Column('redirect_count', sa.Integer(), nullable=False),
    sa.Column('last_redirect', sa.DateTime(), nullable=True),
    sa.Column('expires_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_short_url_expires_at'), 'short_url', ['expires_at'], unique=False)
    op.create_index(op.f('ix_short_url_last_redirect'), 'short_url', ['last_redirect'], unique=False)
    op.create_index(op.f('ix_short_url_original_url'), 'short_url', ['original_url'], unique=False)
    op.create_index(op.f('ix_short_url_short_name'), 'short_url', ['short_name'], unique=True)
    op.create_index(op.f('ix_short_url_user_id'), 'short_url', ['user_id'], unique=False)
    op.create_table('user',
    sa.Column('id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('hashed_password', sa.String(length=1024), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_short_url_user_id'), table_name='short_url')
    op.drop_index(op.f('ix_short_url_short_name'), table_name='short_url')
    op.drop_index(op.f('ix_short_url_original_url'), table_name='short_url')
    op.drop_index(op.f('ix_short_url_last_redirect'), table_name='short_url')
    op.drop_index(op.f('ix_short_url_expires_at'), table_name='short_url')
    op.drop_table('short_url')
    op.drop_index(op.f('ix_events_short_url'), table_name='events')
    op.drop_index(op.f('ix_events_id'), table_name='events')
    op.drop_index(op.f('ix_events_event_type'), table_name='events')
    op.drop_index(op.f('ix_events_datetime'), table_name='events')
    op.drop_table('events')
    # ### end Alembic commands ###
