"""Initial community schema.

Revision ID: 0001
Revises:
"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("username", sa.String(24), nullable=False, unique=True), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("role", sa.String(16), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("sessions", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("token_hash", sa.String(64), nullable=False), sa.Column("csrf_token", sa.String(64), nullable=False), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_sessions_token_hash", "sessions", ["token_hash"], unique=True)
    op.create_table("content", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("title", sa.String(160), nullable=False), sa.Column("body", sa.Text(), nullable=False), sa.Column("format", sa.String(20), nullable=False), sa.Column("topic", sa.String(60), nullable=False), sa.Column("stage", sa.String(60), nullable=False), sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("verified", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True)))
    op.create_table("comments", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("content_id", sa.Integer(), sa.ForeignKey("content.id", ondelete="CASCADE"), nullable=False), sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("body", sa.Text(), nullable=False), sa.Column("parent_id", sa.Integer(), sa.ForeignKey("comments.id")), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True)))
    op.create_table("saves", sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True), sa.Column("content_id", sa.Integer(), sa.ForeignKey("content.id", ondelete="CASCADE"), primary_key=True))
    op.create_table("reactions", sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True), sa.Column("content_id", sa.Integer(), sa.ForeignKey("content.id", ondelete="CASCADE"), primary_key=True))
    op.create_table("events", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("title", sa.String(160), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("kind", sa.String(40), nullable=False), sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False), sa.Column("mode", sa.String(30), nullable=False), sa.Column("host", sa.String(80), nullable=False))
    op.create_table("registrations", sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True), sa.Column("event_id", sa.Integer(), sa.ForeignKey("events.id", ondelete="CASCADE"), primary_key=True))
    op.create_table("activities", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("title", sa.String(160), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("kind", sa.String(30), nullable=False), sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False), sa.Column("location", sa.String(100), nullable=False), sa.Column("organiser_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True)))
    op.create_table("activity_joins", sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True), sa.Column("activity_id", sa.Integer(), sa.ForeignKey("activities.id", ondelete="CASCADE"), primary_key=True))
    op.create_table("community_groups", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(100), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("audience", sa.String(80), nullable=False))
    op.create_table("help_requests", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("requester_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("title", sa.String(120), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("area", sa.String(80), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True)))
    op.create_table("help_offers", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("request_id", sa.Integer(), sa.ForeignKey("help_requests.id", ondelete="CASCADE"), nullable=False), sa.Column("volunteer_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.UniqueConstraint("request_id", "volunteer_id"))
    op.create_table("reports", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("reporter_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("target_type", sa.String(20), nullable=False), sa.Column("target_id", sa.Integer(), nullable=False), sa.Column("reason", sa.String(50), nullable=False), sa.Column("details", sa.Text(), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))


def downgrade():
    for table in ("reports", "help_offers", "help_requests", "community_groups", "activity_joins", "activities", "registrations", "events", "reactions", "saves", "comments", "content", "sessions", "users"):
        op.drop_table(table)
