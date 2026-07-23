"""001 original schema — the 8 tables from the provided PostgreSQL script

Revision ID: 001
Revises:
Create Date: 2026-07-23
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "app_user",
        sa.Column("user_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("employee_id", sa.String(20), unique=True),
        sa.Column("full_name", sa.String(100)),
        sa.Column("email", sa.String(100)),
        sa.Column("department", sa.String(50)),
        sa.Column("role", sa.String(50)),
        sa.Column("location", sa.String(50)),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "incident",
        sa.Column("incident_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("incident_number", sa.String(30)),
        sa.Column("title", sa.String(200)),
        sa.Column("description", sa.Text),
        sa.Column("priority", sa.String(20)),
        sa.Column("status", sa.String(30)),
        sa.Column("affected_users", sa.Integer),
        sa.Column("application", sa.String(100)),
        sa.Column("root_cause", sa.String(200)),
        sa.Column("created_by", sa.Integer, sa.ForeignKey("app_user.user_id")),
        sa.Column("created_at", sa.TIMESTAMP),
        sa.Column("resolved_at", sa.TIMESTAMP, nullable=True),
    )

    op.create_table(
        "ai_agent",
        sa.Column("agent_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("agent_name", sa.String(100)),
        sa.Column("agent_type", sa.String(50)),
        sa.Column("status", sa.String(20)),
        sa.Column("confidence_score", sa.Numeric(5, 2)),
    )

    op.create_table(
        "ai_investigation",
        sa.Column("investigation_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("incident_id", sa.Integer, sa.ForeignKey("incident.incident_id")),
        sa.Column("agent_id", sa.Integer, sa.ForeignKey("ai_agent.agent_id")),
        sa.Column("findings", sa.Text),
        sa.Column("recommendation", sa.Text),
        sa.Column("execution_time", sa.Integer),
    )

    op.create_table(
        "knowledge_article",
        sa.Column("article_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("article_number", sa.String(30)),
        sa.Column("title", sa.String(200)),
        sa.Column("category", sa.String(100)),
        sa.Column("keywords", sa.Text),
        sa.Column("helpful_percentage", sa.Integer),
        sa.Column("updated_date", sa.Date),
    )

    op.create_table(
        "dora_compliance",
        sa.Column("compliance_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("operational_resilience", sa.Numeric(5, 2)),
        sa.Column("ict_risk", sa.Numeric(5, 2)),
        sa.Column("incident_management", sa.Numeric(5, 2)),
        sa.Column("business_continuity", sa.Numeric(5, 2)),
        sa.Column("third_party_risk", sa.Numeric(5, 2)),
        sa.Column("overall_score", sa.Numeric(5, 2)),
        sa.Column("audit_ready", sa.Boolean),
    )

    op.create_table(
        "escalation",
        sa.Column("escalation_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("incident_id", sa.Integer, sa.ForeignKey("incident.incident_id")),
        sa.Column("assigned_team", sa.String(100)),
        sa.Column("engineer_name", sa.String(100)),
        sa.Column("reason", sa.Text),
        sa.Column("estimated_wait", sa.Integer),
        sa.Column("status", sa.String(50)),
    )

    op.create_table(
        "executive_metrics",
        sa.Column("metric_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("metric_date", sa.Date),
        sa.Column("automated_resolution", sa.Numeric(5, 2)),
        sa.Column("manual_escalation", sa.Numeric(5, 2)),
        sa.Column("avg_resolution_minutes", sa.Integer),
        sa.Column("critical_incidents", sa.Integer),
        sa.Column("dora_score", sa.Numeric(5, 2)),
        sa.Column("cyber_hygiene_score", sa.Numeric(5, 2)),
    )


def downgrade():
    op.drop_table("executive_metrics")
    op.drop_table("escalation")
    op.drop_table("dora_compliance")
    op.drop_table("knowledge_article")
    op.drop_table("ai_investigation")
    op.drop_table("ai_agent")
    op.drop_table("incident")
    op.drop_table("app_user")
