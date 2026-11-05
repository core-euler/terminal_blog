"""Регистрация внешних агентов и проверка их ключей."""

from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.config import Settings
from app.errors import Forbidden, InvalidPayload
from app.models import Agent, AgentStatus, AgentToken
from app.security import hash_secret, new_token


def create_agent(
    session: Session, settings: Settings, *, name: str, description: str | None = None
) -> tuple[Agent, str]:
    """Создаёт профиль агента и выдаёт ключ. Открытый ключ возвращается один раз."""
    if session.scalar(sa.select(Agent.id).where(Agent.name == name)) is not None:
        raise InvalidPayload("агент с таким именем уже есть")
    agent = Agent(name=name, description=description)
    session.add(agent)
    session.flush()
    token = issue_token(session, settings, agent)
    session.commit()
    return agent, token


def issue_token(session: Session, settings: Settings, agent: Agent) -> str:
    """Выдаёт новый ключ агенту. В базе остаётся только хеш."""
    token = new_token()
    session.add(AgentToken(agent_id=agent.id, token_hash=hash_secret(token, settings.hash_pepper)))
    session.flush()
    return token


def authenticate(session: Session, settings: Settings, token: str) -> Agent:
    """Проверяет ключ агента. Отозванный ключ и отключённый агент не проходят."""
    if not token:
        raise Forbidden("нужен ключ агента")
    token_hash = hash_secret(token, settings.hash_pepper)
    row = session.execute(
        sa.select(AgentToken, Agent)
        .join(Agent, Agent.id == AgentToken.agent_id)
        .where(AgentToken.token_hash == token_hash)
    ).first()
    if row is None:
        raise Forbidden("ключ не подходит")
    token_row, agent = row
    if token_row.revoked_at is not None:
        raise Forbidden("ключ отозван")
    if agent.status is not AgentStatus.active:
        raise Forbidden("агент отключён")
    return agent


def revoke_token(session: Session, settings: Settings, token: str) -> None:
    """Отзывает ключ. Авторство прошлых комментариев не меняется."""
    token_hash = hash_secret(token, settings.hash_pepper)
    token_row = session.scalar(sa.select(AgentToken).where(AgentToken.token_hash == token_hash))
    if token_row is None:
        raise InvalidPayload("ключ не найден")
    if token_row.revoked_at is None:
        token_row.revoked_at = datetime.now(timezone.utc)
        session.commit()


def revoke_all_tokens(session: Session, agent: Agent) -> None:
    moment = datetime.now(timezone.utc)
    for token_row in session.scalars(sa.select(AgentToken).where(AgentToken.agent_id == agent.id)):
        if token_row.revoked_at is None:
            token_row.revoked_at = moment
    session.commit()


def disable_agent(session: Session, name: str) -> Agent:
    agent = session.scalar(sa.select(Agent).where(Agent.name == name))
    if agent is None:
        raise InvalidPayload("агент не найден")
    agent.status = AgentStatus.disabled
    session.commit()
    return agent
