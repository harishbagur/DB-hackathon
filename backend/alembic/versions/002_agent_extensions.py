"""002 agent extensions — minimal additions for the multi-agent system

Revision ID: 002
Revises: 001
Create Date: 2026-07-23

Changes:
  - Enable pgvector extension
  - incident: 6 new columns for agent state tracking
  - knowledge_article: content, status, embedding, source_incident_id
  - 5 new tables: playbook, chat_room, chat_message, room_agent, room_member
"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    # pgvector extension — one command on the DB
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # --- Extend incident table ---
    op.add_column("incident", sa.Column("platform", sa.String(20), server_default="unix"))
    op.add_column("incident", sa.Column("ci_criticality", sa.String(20), server_default="tier2"))
    op.add_column("incident", sa.Column("classification", sa.String(20), server_default="unknown"))
    op.add_column("incident", sa.Column("classification_confidence", sa.Numeric(5, 2), server_default="0"))
    op.add_column("incident", sa.Column("hop_count", sa.Integer, server_default="0"))
    op.add_column("incident", sa.Column("current_owner", sa.String(50), server_default="incident_lead_agent"))

    # --- Extend knowledge_article table ---
    op.add_column("knowledge_article", sa.Column("content", sa.Text, nullable=True))
    # Existing articles default to 'approved'; agent-created ones start as 'draft'
    op.add_column("knowledge_article", sa.Column("status", sa.String(20), server_default="approved"))
    op.add_column("knowledge_article", sa.Column("source_incident_id", sa.Integer, nullable=True))
    # 384 dimensions — matches all-MiniLM-L6-v2 from sentence-transformers
    op.add_column("knowledge_article", sa.Column("embedding", Vector(384), nullable=True))

    # --- New: playbook table ---
    op.create_table(
        "playbook",
        sa.Column("playbook_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100)),
        sa.Column("platform", sa.String(20)),       # unix / windows / any
        sa.Column("trigger_keywords", sa.Text),     # comma-separated
        sa.Column("action_tier", sa.Integer),        # 0 / 1 / 2 / 3
        sa.Column("script", sa.Text),
        sa.Column("verify_command", sa.Text),
        sa.Column("description", sa.Text),
        sa.Column("success_count", sa.Integer, server_default="0"),
        sa.Column("failure_count", sa.Integer, server_default="0"),
    )

    # --- New: chat room tables ---
    op.create_table(
        "chat_room",
        sa.Column("room_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("incident_id", sa.Integer, sa.ForeignKey("incident.incident_id"), unique=True),
        sa.Column("status", sa.String(20), server_default="open"),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "chat_message",
        sa.Column("message_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("room_id", sa.Integer, sa.ForeignKey("chat_room.room_id")),
        sa.Column("sender_type", sa.String(10)),    # agent / user
        sa.Column("sender_id", sa.Integer),
        sa.Column("sender_name", sa.String(100)),
        sa.Column("content", sa.Text),
        # text / article_list / approval_request / system
        sa.Column("message_type", sa.String(30), server_default="text"),
        sa.Column("metadata_json", sa.Text, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "room_agent",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("room_id", sa.Integer, sa.ForeignKey("chat_room.room_id")),
        sa.Column("agent_id", sa.Integer, sa.ForeignKey("ai_agent.agent_id")),
        sa.Column("added_at", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "room_member",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("room_id", sa.Integer, sa.ForeignKey("chat_room.room_id")),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("app_user.user_id")),
        sa.Column("added_at", sa.TIMESTAMP, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("room_member")
    op.drop_table("room_agent")
    op.drop_table("chat_message")
    op.drop_table("chat_room")
    op.drop_table("playbook")
    op.drop_column("knowledge_article", "embedding")
    op.drop_column("knowledge_article", "source_incident_id")
    op.drop_column("knowledge_article", "status")
    op.drop_column("knowledge_article", "content")
    op.drop_column("incident", "current_owner")
    op.drop_column("incident", "hop_count")
    op.drop_column("incident", "classification_confidence")
    op.drop_column("incident", "classification")
    op.drop_column("incident", "ci_criticality")
    op.drop_column("incident", "platform")
    op.execute("DROP EXTENSION IF EXISTS vector")
