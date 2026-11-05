"""Состояние агента новостей: источники, записи лент, журнал запусков, замок.

Revision ID: 0002
Revises: 0001
"""

from alembic import op
import sqlalchemy as sa


revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('agent_locks',
    sa.Column('name', sa.String(length=60), nullable=False),
    sa.Column('owner', sa.String(length=60), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('agent_runs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('sources_polled', sa.Integer(), nullable=False),
    sa.Column('items_received', sa.Integer(), nullable=False),
    sa.Column('items_selected', sa.Integer(), nullable=False),
    sa.Column('items_drafted', sa.Integer(), nullable=False),
    sa.Column('items_published', sa.Integer(), nullable=False),
    sa.Column('error', sa.String(length=300), nullable=True),
    sa.Column('details', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_runs_started_at'), 'agent_runs', ['started_at'], unique=False)
    op.create_table('feed_sources',
    sa.Column('key', sa.String(length=120), nullable=False),
    sa.Column('etag', sa.String(length=300), nullable=True),
    sa.Column('last_modified', sa.String(length=200), nullable=True),
    sa.Column('last_ok_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('consecutive_errors', sa.Integer(), nullable=False),
    sa.Column('paused_until', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_error', sa.String(length=300), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('key')
    )
    op.create_table('feed_items',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('source_key', sa.String(length=120), nullable=False),
    sa.Column('external_id', sa.String(length=400), nullable=False),
    sa.Column('url', sa.String(length=1000), nullable=False),
    sa.Column('canonical_url', sa.String(length=1000), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('summary', sa.Text(), nullable=False),
    sa.Column('fingerprint', sa.String(length=200), nullable=False),
    sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('seen_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('status', sa.Enum('new', 'skipped', 'failed', 'drafted', 'published', name='feeditemstatus', native_enum=False, length=24), nullable=False),
    sa.Column('skip_reason', sa.String(length=40), nullable=True),
    sa.Column('attempts', sa.Integer(), nullable=False),
    sa.Column('last_error', sa.String(length=300), nullable=True),
    sa.Column('news_id', sa.Uuid(), nullable=True),
    sa.ForeignKeyConstraint(['news_id'], ['news.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('source_key', 'external_id', name='uq_feed_items_source_external')
    )
    op.create_index(op.f('ix_feed_items_canonical_url'), 'feed_items', ['canonical_url'], unique=False)
    op.create_index(op.f('ix_feed_items_fingerprint'), 'feed_items', ['fingerprint'], unique=False)
    op.create_index(op.f('ix_feed_items_news_id'), 'feed_items', ['news_id'], unique=False)
    op.create_index(op.f('ix_feed_items_source_key'), 'feed_items', ['source_key'], unique=False)
    op.create_index(op.f('ix_feed_items_status'), 'feed_items', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_feed_items_status'), table_name='feed_items')
    op.drop_index(op.f('ix_feed_items_source_key'), table_name='feed_items')
    op.drop_index(op.f('ix_feed_items_news_id'), table_name='feed_items')
    op.drop_index(op.f('ix_feed_items_fingerprint'), table_name='feed_items')
    op.drop_index(op.f('ix_feed_items_canonical_url'), table_name='feed_items')
    op.drop_table('feed_items')
    op.drop_table('feed_sources')
    op.drop_index(op.f('ix_agent_runs_started_at'), table_name='agent_runs')
    op.drop_table('agent_runs')
    op.drop_table('agent_locks')
