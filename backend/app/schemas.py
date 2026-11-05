"""Схемы запросов и ответов."""

from datetime import date, datetime

from pydantic import BaseModel, Field


class SourceIn(BaseModel):
    url: str = Field(min_length=8, max_length=1000)
    title: str | None = Field(default=None, max_length=300)


class NewsPublishIn(BaseModel):
    external_id: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=200, pattern=r"^[^\s/\\?#]+$")
    title: str = Field(min_length=3, max_length=300)
    body: str = Field(min_length=1, max_length=20000)
    topic: str = Field(min_length=2, max_length=40)
    event_date: date
    sources: list[SourceIn] = Field(min_length=1, max_length=20)


class SourceOut(BaseModel):
    url: str
    title: str | None


class NewsOut(BaseModel):
    id: str
    slug: str
    title: str
    body: str
    topic: str
    event_date: date
    published_at: datetime
    sources: list[SourceOut]


class NewsListOut(BaseModel):
    items: list[NewsOut]
    total: int
    limit: int
    offset: int


class CommentIn(BaseModel):
    text: str = Field(min_length=1)
    name: str | None = Field(default=None, max_length=200)
    client_id: str | None = Field(default=None, min_length=8, max_length=64, pattern=r"^[A-Za-z0-9._-]+$")


class CommentAuthorOut(BaseModel):
    kind: str
    name: str


class CommentOut(BaseModel):
    id: str
    author: CommentAuthorOut
    text: str
    created_at: datetime


class CommentListOut(BaseModel):
    items: list[CommentOut]


class CommentCreatedOut(BaseModel):
    id: str
    status: str
    message: str
