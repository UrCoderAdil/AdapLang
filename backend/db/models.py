"""SQLAlchemy ORM models for the Language RPG."""
from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship


def _now():
    return datetime.now(timezone.utc)


def _uuid():
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    email = Column(Text, unique=True, nullable=False)
    display_name = Column(String(64))
    created_at = Column(DateTime(timezone=True), default=_now)
    streak = Column(Integer, default=0, nullable=False)
    last_active_date = Column(Date, nullable=True)
    total_xp = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    freeze_items = Column(Integer, default=0, nullable=False)
    current_world = Column(Integer, default=1, nullable=False)
    beaten_worlds = Column(JSONB, default=list)
    achievement_ids = Column(JSONB, default=list)

    skill_states = relationship("UserSkillState", back_populates="user", cascade="all, delete-orphan")
    responses = relationship("Response", back_populates="user", cascade="all, delete-orphan")
    question_states = relationship("UserQuestionState", back_populates="user", cascade="all, delete-orphan")


class UserSkillState(Base):
    __tablename__ = "user_skill_states"
    __table_args__ = (UniqueConstraint("user_id", "skill_tag"),)

    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    skill_tag = Column(Text, primary_key=True)
    theta = Column(Float, default=0.0, nullable=False)
    sigma = Column(Float, default=1.0, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)

    user = relationship("User", back_populates="skill_states")


class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    language = Column(Text, nullable=False)
    cefr_level = Column(String(2), nullable=False)
    skill_tag = Column(Text, nullable=False)
    question = Column(Text, nullable=False)
    options = Column(JSONB, nullable=False)
    correct_index = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=False)
    b = Column(Float, nullable=False)
    a = Column(Float, default=1.0, nullable=False)
    c = Column(Float, default=0.25, nullable=False)
    quality_score = Column(Float, nullable=True)
    world_id = Column(Integer, nullable=True)
    is_boss_question = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=_now)

    responses = relationship("Response", back_populates="question")
    user_states = relationship("UserQuestionState", back_populates="question")


class Response(Base):
    __tablename__ = "responses"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(UUID(as_uuid=False), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    correct = Column(Boolean, nullable=False)
    response_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)

    user = relationship("User", back_populates="responses")
    question = relationship("Question", back_populates="responses")


class UserQuestionState(Base):
    __tablename__ = "user_question_states"
    __table_args__ = (UniqueConstraint("user_id", "question_id"),)

    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    question_id = Column(UUID(as_uuid=False), ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True)
    fsrs_card_state = Column(JSONB, nullable=True)
    next_review_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="question_states")
    question = relationship("Question", back_populates="user_states")


# Indexes (defined after models for clarity)
Index("ix_questions_language_cefr", Question.language, Question.cefr_level)
Index("ix_questions_skill", Question.skill_tag)
Index("ix_uqs_next_review", UserQuestionState.user_id, UserQuestionState.next_review_at)
Index("ix_responses_question", Response.question_id)
Index("ix_responses_user", Response.user_id)
