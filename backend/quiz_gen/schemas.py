"""Pydantic schemas for generated questions."""
from typing import Literal
from pydantic import BaseModel, Field, field_validator


class Question(BaseModel):
    question: str = Field(..., description="The question text shown to the learner.")
    options: list[str] = Field(..., min_length=4, max_length=4, description="Exactly 4 answer options.")
    correct_index: int = Field(..., ge=0, le=3, description="Index of the correct option (0–3).")
    explanation: str = Field(..., description="Teaching explanation shown after answering.")
    cefr_level: Literal["A1", "A2", "B1", "B2", "C1", "C2"]
    skill_tag: str = Field(..., description="e.g. 'past_tense', 'vocabulary_food'")
    language: str = Field(..., description="Target language, e.g. 'spanish'")
    estimated_difficulty_b: float = Field(
        ..., ge=-3.0, le=3.0, description="IRT difficulty estimate on theta scale."
    )

    @field_validator("options")
    @classmethod
    def options_must_be_unique(cls, v: list[str]) -> list[str]:
        if len(set(v)) != len(v):
            raise ValueError("All options must be unique.")
        return v


class QuestionInDB(Question):
    id: str
    quality_score: float | None = None
    embedding: list[float] | None = None

    class Config:
        from_attributes = True


class QuestionGenerationRequest(BaseModel):
    language: str
    cefr_level: Literal["A1", "A2", "B1", "B2", "C1", "C2"]
    skill_tag: str
    count: int = Field(1, ge=1, le=20)


class QualityScoreResult(BaseModel):
    score: float = Field(..., ge=0.0, le=10.0)
    reason: str
