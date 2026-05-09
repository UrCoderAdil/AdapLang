"""
Auto-QA: run a second LLM pass to score every generated question.
Questions scoring below MIN_QUALITY_SCORE are discarded.
"""
import os
import json
import logging

from .schemas import Question, QualityScoreResult

logger = logging.getLogger(__name__)

MIN_QUALITY_SCORE = 7.0


def quality_score(question: Question) -> QualityScoreResult:
    """
    Score a question 0–10 via Claude.
    Returns a QualityScoreResult with score and reason.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return QualityScoreResult(score=8.0, reason="Stub score (no API key).")

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        prompt = f"""Rate this language learning question on a scale of 0–10.

Criteria:
1. Grammatical accuracy of all options
2. Distractor plausibility (wrong options must look plausible)
3. Explanation quality (must teach, not just reveal answer)
4. Difficulty appropriateness for stated CEFR level

Return ONLY valid JSON: {{"score": <float>, "reason": "<one sentence>"}}

Question:
{question.model_dump_json(indent=2)}"""

        message = client.messages.create(
            model="claude-haiku-4-20250514",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        data = json.loads(raw)
        return QualityScoreResult(**data)

    except Exception as exc:
        logger.error("Quality scoring failed: %s", exc)
        return QualityScoreResult(score=5.0, reason=f"Scoring error: {exc}")


def passes_quality_bar(question: Question) -> tuple[bool, QualityScoreResult]:
    result = quality_score(question)
    return result.score >= MIN_QUALITY_SCORE, result
