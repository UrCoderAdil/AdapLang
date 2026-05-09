"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-09
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=False), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("email", sa.Text, unique=True, nullable=False),
        sa.Column("display_name", sa.String(64)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("streak", sa.Integer, server_default=sa.text("0"), nullable=False),
        sa.Column("last_active_date", sa.Date),
        sa.Column("total_xp", sa.Integer, server_default=sa.text("0"), nullable=False),
        sa.Column("level", sa.Integer, server_default=sa.text("1"), nullable=False),
        sa.Column("freeze_items", sa.Integer, server_default=sa.text("0"), nullable=False),
        sa.Column("current_world", sa.Integer, server_default=sa.text("1"), nullable=False),
        sa.Column("beaten_worlds", JSONB, server_default=sa.text("'[]'::jsonb")),
        sa.Column("achievement_ids", JSONB, server_default=sa.text("'[]'::jsonb")),
    )

    op.create_table(
        "user_skill_states",
        sa.Column("user_id", UUID(as_uuid=False), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("skill_tag", sa.Text, primary_key=True),
        sa.Column("theta", sa.Float, server_default=sa.text("0.0"), nullable=False),
        sa.Column("sigma", sa.Float, server_default=sa.text("1.0"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )

    op.create_table(
        "questions",
        sa.Column("id", UUID(as_uuid=False), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("language", sa.Text, nullable=False),
        sa.Column("cefr_level", sa.String(2), nullable=False),
        sa.Column("skill_tag", sa.Text, nullable=False),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("options", JSONB, nullable=False),
        sa.Column("correct_index", sa.Integer, nullable=False),
        sa.Column("explanation", sa.Text, nullable=False),
        sa.Column("b", sa.Float, nullable=False),
        sa.Column("a", sa.Float, server_default=sa.text("1.0"), nullable=False),
        sa.Column("c", sa.Float, server_default=sa.text("0.25"), nullable=False),
        sa.Column("quality_score", sa.Float),
        sa.Column("world_id", sa.Integer),
        sa.Column("is_boss_question", sa.Boolean, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.execute("ALTER TABLE questions ADD COLUMN IF NOT EXISTS embedding vector(384)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_questions_embedding ON questions USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)")
    op.create_index("ix_questions_language_cefr", "questions", ["language", "cefr_level"])
    op.create_index("ix_questions_skill", "questions", ["skill_tag"])

    op.create_table(
        "responses",
        sa.Column("id", UUID(as_uuid=False), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", UUID(as_uuid=False), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_id", UUID(as_uuid=False), sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("correct", sa.Boolean, nullable=False),
        sa.Column("response_time_ms", sa.Integer),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_responses_question", "responses", ["question_id"])
    op.create_index("ix_responses_user", "responses", ["user_id"])

    op.create_table(
        "user_question_states",
        sa.Column("user_id", UUID(as_uuid=False), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("question_id", UUID(as_uuid=False), sa.ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("fsrs_card_state", JSONB),
        sa.Column("next_review_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_uqs_next_review", "user_question_states", ["user_id", "next_review_at"])


def downgrade() -> None:
    op.drop_table("user_question_states")
    op.drop_table("responses")
    op.drop_table("questions")
    op.drop_table("user_skill_states")
    op.drop_table("users")
