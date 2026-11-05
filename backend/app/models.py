"""Схема данных. Типы переносимые: те же модели работают на PostgreSQL и SQLite."""

import enum
import uuid
from datetime import date, datetime, timezone

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class NewsStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    hidden = "hidden"


class CommentStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class AuthorKind(str, enum.Enum):
    human = "human"
    agent = "agent"


class AgentStatus(str, enum.Enum):
    active = "active"
    disabled = "disabled"


class FeedItemStatus(str, enum.Enum):
    new = "new"
    skipped = "skipped"
    failed = "failed"
    drafted = "drafted"
    published = "published"


class ModerationDecision(str, enum.Enum):
    approved = "approved"
    rejected = "rejected"


def _enum(enum_cls: type[enum.Enum], length: int = 24) -> sa.Enum:
    return sa.Enum(
        enum_cls,
        native_enum=False,
        length=length,
        values_callable=lambda e: [member.value for member in e],
    )


def _now() -> datetime:
    return datetime.now(timezone.utc)


class News(Base):
    __tablename__ = "news"

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(sa.String(200), unique=True, index=True)
    title: Mapped[str] = mapped_column(sa.String(300))
    body: Mapped[str] = mapped_column(sa.Text)
    topic: Mapped[str] = mapped_column(sa.String(40), index=True)
    event_date: Mapped[date] = mapped_column(sa.Date)
    external_id: Mapped[str] = mapped_column(sa.String(200), unique=True)
    status: Mapped[NewsStatus] = mapped_column(_enum(NewsStatus), default=NewsStatus.draft, index=True)
    published_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=_now)

    sources: Mapped[list["NewsSource"]] = relationship(
        back_populates="news", cascade="all, delete-orphan", order_by="NewsSource.id"
    )


class NewsSource(Base):
    __tablename__ = "news_sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    news_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("news.id", ondelete="CASCADE"), index=True)
    url: Mapped[str] = mapped_column(sa.String(1000))
    title: Mapped[str | None] = mapped_column(sa.String(300), nullable=True)

    news: Mapped[News] = relationship(back_populates="sources")


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(sa.String(120), unique=True)
    description: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    status: Mapped[AgentStatus] = mapped_column(_enum(AgentStatus), default=AgentStatus.active)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=_now)

    tokens: Mapped[list["AgentToken"]] = relationship(back_populates="agent", cascade="all, delete-orphan")


class AgentToken(Base):
    __tablename__ = "agent_tokens"

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("agents.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(sa.String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=_now)
    revoked_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    agent: Mapped[Agent] = relationship(back_populates="tokens")


class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = (
        sa.CheckConstraint(
            "(kind = 'human' AND agent_id IS NULL) OR (kind = 'agent' AND agent_id IS NOT NULL)",
            name="ck_comments_author_kind",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    news_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("news.id", ondelete="CASCADE"), index=True)
    kind: Mapped[AuthorKind] = mapped_column(_enum(AuthorKind))
    display_name: Mapped[str | None] = mapped_column(sa.String(40), nullable=True)
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("agents.id", ondelete="SET NULL"), nullable=True
    )
    text: Mapped[str] = mapped_column(sa.Text)
    status: Mapped[CommentStatus] = mapped_column(_enum(CommentStatus), default=CommentStatus.pending, index=True)
    attempts: Mapped[int] = mapped_column(default=0)
    last_error: Mapped[str | None] = mapped_column(sa.String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=_now, index=True)
    decided_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    agent: Mapped[Agent | None] = relationship()


class ModerationEvent(Base):
    __tablename__ = "moderation_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    comment_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("comments.id", ondelete="CASCADE"), index=True)
    decision: Mapped[ModerationDecision] = mapped_column(_enum(ModerationDecision))
    reason: Mapped[str] = mapped_column(sa.String(500))
    rules_version: Mapped[str] = mapped_column(sa.String(40))
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=_now)


class RateEvent(Base):
    __tablename__ = "rate_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_hash: Mapped[str] = mapped_column(sa.String(64), index=True)
    kind: Mapped[str] = mapped_column(sa.String(16))
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=_now, index=True)


class FeedSourceState(Base):
    """Состояние опроса источника. Сама конфигурация источника живёт в файле."""

    __tablename__ = "feed_sources"

    key: Mapped[str] = mapped_column(sa.String(120), primary_key=True)
    etag: Mapped[str | None] = mapped_column(sa.String(300), nullable=True)
    last_modified: Mapped[str | None] = mapped_column(sa.String(200), nullable=True)
    last_ok_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    consecutive_errors: Mapped[int] = mapped_column(default=0)
    paused_until: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(sa.String(300), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=_now)


class FeedItem(Base):
    """Запись ленты. Хранится, чтобы повторный запуск не создавал второй новости."""

    __tablename__ = "feed_items"
    __table_args__ = (sa.UniqueConstraint("source_key", "external_id", name="uq_feed_items_source_external"),)

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    source_key: Mapped[str] = mapped_column(sa.String(120), index=True)
    external_id: Mapped[str] = mapped_column(sa.String(400))
    url: Mapped[str] = mapped_column(sa.String(1000))
    canonical_url: Mapped[str] = mapped_column(sa.String(1000), index=True)
    title: Mapped[str] = mapped_column(sa.String(500))
    summary: Mapped[str] = mapped_column(sa.Text)
    fingerprint: Mapped[str] = mapped_column(sa.String(200), index=True)
    published_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    seen_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=_now)
    status: Mapped[FeedItemStatus] = mapped_column(_enum(FeedItemStatus), default=FeedItemStatus.new, index=True)
    skip_reason: Mapped[str | None] = mapped_column(sa.String(40), nullable=True)
    attempts: Mapped[int] = mapped_column(default=0)
    last_error: Mapped[str | None] = mapped_column(sa.String(300), nullable=True)
    news_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("news.id", ondelete="SET NULL"), nullable=True, index=True
    )


class AgentRun(Base):
    """Журнал запусков агента новостей."""

    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    started_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=_now, index=True)
    finished_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    sources_polled: Mapped[int] = mapped_column(default=0)
    items_received: Mapped[int] = mapped_column(default=0)
    items_selected: Mapped[int] = mapped_column(default=0)
    items_drafted: Mapped[int] = mapped_column(default=0)
    items_published: Mapped[int] = mapped_column(default=0)
    error: Mapped[str | None] = mapped_column(sa.String(300), nullable=True)
    details: Mapped[str | None] = mapped_column(sa.Text, nullable=True)


class AgentLock(Base):
    """Замок цикла: второй запуск не начинается, пока держится первый."""

    __tablename__ = "agent_locks"

    name: Mapped[str] = mapped_column(sa.String(60), primary_key=True)
    owner: Mapped[str] = mapped_column(sa.String(60))
    expires_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True))
