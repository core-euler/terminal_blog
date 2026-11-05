"""Миграции создают ту же схему, что описана моделями."""

from alembic import command
from sqlalchemy import inspect

from app.models import Base
from conftest import alembic_config, drop_schema


def _tables(engine) -> set[str]:
    return set(inspect(engine).get_table_names())


def test_upgrade_head_builds_schema_from_scratch(engine, settings):
    drop_schema(engine)
    assert _tables(engine) == set()

    command.upgrade(alembic_config(settings.database_url), "head")

    expected = {table.name for table in Base.metadata.sorted_tables}
    assert expected <= _tables(engine)

    for table in Base.metadata.sorted_tables:
        migrated = {column["name"] for column in inspect(engine).get_columns(table.name)}
        assert migrated == {column.name for column in table.columns}, table.name


def test_downgrade_removes_schema(engine, settings):
    config = alembic_config(settings.database_url)
    command.downgrade(config, "base")

    assert not {table.name for table in Base.metadata.sorted_tables} & _tables(engine)

    command.upgrade(config, "head")
    assert {table.name for table in Base.metadata.sorted_tables} <= _tables(engine)
