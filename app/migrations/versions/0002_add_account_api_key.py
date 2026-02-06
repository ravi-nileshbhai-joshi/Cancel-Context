"""add account api key

Revision ID: 0002_add_account_api_key
Revises: 0001_initial
Create Date: 2026-02-06

"""
from alembic import op
import sqlalchemy as sa


revision = "0002_add_account_api_key"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("accounts", sa.Column("api_key", sa.String(length=64), nullable=True))
    op.create_index("ix_accounts_api_key", "accounts", ["api_key"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_accounts_api_key", table_name="accounts")
    op.drop_column("accounts", "api_key")
