"""Add ownership to posts.

Revision ID: 0003_add_post_owner
Revises: 0002_create_users
Create Date: 2026-10-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003_add_post_owner"
down_revision: Union[str, Sequence[str], None] = "0002_create_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("posts", sa.Column("owner_id", sa.Integer(), nullable=False))
    op.create_foreign_key(
        "fk_posts_owner_id_users",
        "posts",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_posts_owner_id_users", "posts", type_="foreignkey")
    op.drop_column("posts", "owner_id")
