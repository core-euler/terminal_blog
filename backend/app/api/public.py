"""Публичные операции: чтение новостей и комментарии."""

from typing import Annotated

from fastapi import APIRouter, Header, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import client_ip
from app.config import Settings
from app.models import Comment
from app.schemas import (
    CommentAuthorOut,
    CommentCreatedOut,
    CommentIn,
    CommentListOut,
    CommentOut,
    NewsListOut,
    NewsOut,
    SourceOut,
)
from app.service import comments as comments_service
from app.service import news as news_service

router = APIRouter(tags=["public"])


def news_out(news) -> NewsOut:
    return NewsOut(
        id=str(news.id),
        slug=news.slug,
        title=news.title,
        body=news.body,
        topic=news.topic,
        event_date=news.event_date,
        published_at=news.published_at,
        sources=[SourceOut(url=source.url, title=source.title) for source in news.sources],
    )


def comment_out(comment: Comment) -> CommentOut:
    if comment.agent is not None:
        author = CommentAuthorOut(kind="agent", name=comment.agent.name)
    else:
        author = CommentAuthorOut(kind="human", name=comment.display_name or "аноним")
    return CommentOut(id=str(comment.id), author=author, text=comment.text, created_at=comment.created_at)


@router.get("/news", response_model=NewsListOut)
def list_news(
    request: Request,
    limit: Annotated[int | None, Query(ge=1, le=50)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> NewsListOut:
    settings: Settings = request.app.state.settings
    page_limit = limit or settings.news_page_limit
    with Session(request.app.state.engine) as session:
        items = news_service.list_published(session, limit=page_limit, offset=offset)
        total = news_service.count_published(session)
        return NewsListOut(
            items=[news_out(item) for item in items], total=total, limit=page_limit, offset=offset
        )


@router.get("/news/{slug}", response_model=NewsOut)
def get_news(slug: str, request: Request) -> NewsOut:
    with Session(request.app.state.engine) as session:
        return news_out(news_service.get_published(session, slug))


@router.get("/news/{slug}/comments", response_model=CommentListOut)
def list_comments(
    slug: str,
    request: Request,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> CommentListOut:
    with Session(request.app.state.engine) as session:
        items = comments_service.list_approved(session, slug=slug, limit=limit, offset=offset)
        return CommentListOut(items=[comment_out(item) for item in items])


@router.post("/news/{slug}/comments", response_model=CommentCreatedOut, status_code=202)
def post_comment(
    slug: str,
    payload: CommentIn,
    request: Request,
    agent_key: Annotated[str | None, Header(alias="X-Agent-Key")] = None,
    idempotency_key: Annotated[str | None, Header(alias="X-Idempotency-Key")] = None,
) -> CommentCreatedOut:
    settings: Settings = request.app.state.settings
    client_id = idempotency_key or payload.client_id
    with Session(request.app.state.engine) as session:
        comment = comments_service.create_comment(
            session,
            settings,
            slug=slug,
            text=payload.text,
            name=payload.name,
            agent_token=agent_key,
            client_ip=client_ip(request, settings),
            client_id=client_id,
        )
        return CommentCreatedOut(
            id=str(comment.id),
            status=comment.status.value,
            message="комментарий принят и ждёт проверки",
        )
