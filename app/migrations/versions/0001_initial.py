"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-02-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("founder_email", sa.String(length=255), nullable=False),
        sa.Column("slack_webhook_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )

    op.create_table(
        "cancellations",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("account_id", sa.String(length=36), nullable=False),
        sa.Column("reason", sa.String(length=50), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("last_page", sa.String(length=500), nullable=True),
        sa.Column("last_events", sa.Text(), nullable=True),
        sa.Column("session_duration_seconds", sa.Integer(), nullable=True),
        sa.Column("browser", sa.String(length=200), nullable=True),
        sa.Column("os", sa.String(length=200), nullable=True),
        sa.Column("js_errors", sa.Text(), nullable=True),
        sa.Column("time_to_first_value_seconds", sa.Integer(), nullable=True),
        sa.Column("raw_context", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_cancellations_account_id", "cancellations", ["account_id"])

    op.create_table(
        "notification_events",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("cancellation_id", sa.String(length=36), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["cancellation_id"], ["cancellations.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_notification_events_cancellation_id", "notification_events", ["cancellation_id"])


def downgrade() -> None:
    op.drop_index("ix_notification_events_cancellation_id", table_name="notification_events")
    op.drop_table("notification_events")
    op.drop_index("ix_cancellations_account_id", table_name="cancellations")
    op.drop_table("cancellations")
    op.drop_table("accounts")
