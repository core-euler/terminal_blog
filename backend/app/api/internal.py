"""Закрытые операции агента новостей."""

from typing import Annotated

from fastapi import APIRouter, Header, Request, Response
from sqlalchemy.orm import Session

from app.api.public import news_out
from app.config import Settings
from app.schemas import NewsOut, NewsPublishIn
from app.service import news as news_service

router = APIRouter(tags=["internal"])


@router.post("/internal/news", response_model=NewsOut)
def publish_news(
    payload: NewsPublishIn,
    request: Request,
    response: Response,
    news_token: Annotated[str | None, Header(alias="X-News-Token")] = None,
) -> NewsOut:
    settings: Settings = request.app.state.settings
    news_service.check_news_token(settings, news_token)
    with Session(request.app.state.engine) as session:
        news, created = news_service.publish_news(
            session,
            settings,
            external_id=payload.external_id,
            slug=payload.slug,
            title=payload.title,
            body=payload.body,
            topic=payload.topic,
            event_date=payload.event_date,
            sources=[(source.url, source.title) for source in payload.sources],
        )
        response.status_code = 201 if created else 200
        return news_out(news)
