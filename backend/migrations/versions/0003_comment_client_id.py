"""Идентификатор клиента у комментария: повторная отправка не создаёт дубль.

Revision ID: 0003
Revises: 0002
"""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("comments", sa.Column("client_id", sa.String(length=64), nullable=True))
    op.create_index("ix_comments_client_id", "comments", ["client_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_comments_client_id", table_name="comments")
    op.drop_column("comments", "client_id")
