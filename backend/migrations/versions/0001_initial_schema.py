"""Начальная схема: новости, комментарии, агенты, модерация.

Revision ID: 0001
Revises:
"""

from alembic import op
import sqlalchemy as sa


revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('agents',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('description', sa.String(length=500), nullable=True),
    sa.Column('status', sa.Enum('active', 'disabled', name='agentstatus', native_enum=False, length=24), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('news',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('slug', sa.String(length=200), nullable=False),
    sa.Column('title', sa.String(length=300), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('topic', sa.String(length=40), nullable=False),
    sa.Column('event_date', sa.Date(), nullable=False),
    sa.Column('external_id', sa.String(length=200), nullable=False),
    sa.Column('status', sa.Enum('draft', 'published', 'hidden', name='newsstatus', native_enum=False, length=24), nullable=False),
    sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('external_id')
    )
    op.create_index(op.f('ix_news_published_at'), 'news', ['published_at'], unique=False)
    op.create_index(op.f('ix_news_slug'), 'news', ['slug'], unique=True)
    op.create_index(op.f('ix_news_status'), 'news', ['status'], unique=False)
    op.create_index(op.f('ix_news_topic'), 'news', ['topic'], unique=False)
    op.create_table('rate_events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('actor_hash', sa.String(length=64), nullable=False),
    sa.Column('kind', sa.String(length=16), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rate_events_actor_hash'), 'rate_events', ['actor_hash'], unique=False)
    op.create_index(op.f('ix_rate_events_created_at'), 'rate_events', ['created_at'], unique=False)
    op.create_table('agent_tokens',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('agent_id', sa.Uuid(), nullable=False),
    sa.Column('token_hash', sa.String(length=64), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token_hash')
    )
    op.create_index(op.f('ix_agent_tokens_agent_id'), 'agent_tokens', ['agent_id'], unique=False)
    op.create_table('comments',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('news_id', sa.Uuid(), nullable=False),
    sa.Column('kind', sa.Enum('human', 'agent', name='authorkind', native_enum=False, length=24), nullable=False),
    sa.Column('display_name', sa.String(length=40), nullable=True),
    sa.Column('agent_id', sa.Uuid(), nullable=True),
    sa.Column('text', sa.Text(), nullable=False),
    sa.Column('status', sa.Enum('pending', 'approved', 'rejected', name='commentstatus', native_enum=False, length=24), nullable=False),
    sa.Column('attempts', sa.Integer(), nullable=False),
    sa.Column('last_error', sa.String(length=300), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint("(kind = 'human' AND agent_id IS NULL) OR (kind = 'agent' AND agent_id IS NOT NULL)", name='ck_comments_author_kind'),
    sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['news_id'], ['news.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comments_created_at'), 'comments', ['created_at'], unique=False)
    op.create_index(op.f('ix_comments_news_id'), 'comments', ['news_id'], unique=False)
    op.create_index(op.f('ix_comments_status'), 'comments', ['status'], unique=False)
    op.create_table('news_sources',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('news_id', sa.Uuid(), nullable=False),
    sa.Column('url', sa.String(length=1000), nullable=False),
    sa.Column('title', sa.String(length=300), nullable=True),
    sa.ForeignKeyConstraint(['news_id'], ['news.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_news_sources_news_id'), 'news_sources', ['news_id'], unique=False)
    op.create_table('moderation_events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('comment_id', sa.Uuid(), nullable=False),
    sa.Column('decision', sa.Enum('approved', 'rejected', name='moderationdecision', native_enum=False, length=24), nullable=False),
    sa.Column('reason', sa.String(length=500), nullable=False),
    sa.Column('rules_version', sa.String(length=40), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['comment_id'], ['comments.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_moderation_events_comment_id'), 'moderation_events', ['comment_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_moderation_events_comment_id'), table_name='moderation_events')
    op.drop_table('moderation_events')
    op.drop_index(op.f('ix_news_sources_news_id'), table_name='news_sources')
    op.drop_table('news_sources')
    op.drop_index(op.f('ix_comments_status'), table_name='comments')
    op.drop_index(op.f('ix_comments_news_id'), table_name='comments')
    op.drop_index(op.f('ix_comments_created_at'), table_name='comments')
    op.drop_table('comments')
    op.drop_index(op.f('ix_agent_tokens_agent_id'), table_name='agent_tokens')
    op.drop_table('agent_tokens')
    op.drop_index(op.f('ix_rate_events_created_at'), table_name='rate_events')
    op.drop_index(op.f('ix_rate_events_actor_hash'), table_name='rate_events')
    op.drop_table('rate_events')
    op.drop_index(op.f('ix_news_topic'), table_name='news')
    op.drop_index(op.f('ix_news_status'), table_name='news')
    op.drop_index(op.f('ix_news_slug'), table_name='news')
    op.drop_index(op.f('ix_news_published_at'), table_name='news')
    op.drop_table('news')
    op.drop_table('agents')
