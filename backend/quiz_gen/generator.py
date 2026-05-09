"""
LLM-powered question generation using Anthropic Claude + instructor.
Falls back to a template-based stub when the API key is not set.
"""
import os
import json
import logging

from .schemas import Question

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = """You are an expert {language} language teacher and psychometrician.
Generate a single multiple-choice question for a {language} learner at CEFR level {cefr_level},
testing the skill: {skill_tag}.

Rules:
- All 4 options must be plausible (no obviously wrong answers)
- The explanation must teach, not just state the answer
- Difficulty must match {cefr_level} precisely
- Return only valid JSON matching the schema exactly
"""


def _build_system_prompt(language: str, cefr_level: str, skill_tag: str) -> str:
    return SYSTEM_PROMPT_TEMPLATE.format(
        language=language, cefr_level=cefr_level, skill_tag=skill_tag
    )


def generate_question(
    language: str,
    cefr_level: str,
    skill_tag: str,
    examples: list[str] | None = None,
) -> Question:
    """
    Generate a single question via Claude.
    Requires ANTHROPIC_API_KEY in environment.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning("ANTHROPIC_API_KEY not set — returning stub question.")
        return _stub_question(language, cefr_level, skill_tag)

    try:
        import anthropic
        import instructor

        client = instructor.from_anthropic(anthropic.Anthropic(api_key=api_key))

        system = _build_system_prompt(language, cefr_level, skill_tag)
        user_msg = f"Generate a {cefr_level} {language} question on the skill: {skill_tag}."
        if examples:
            user_msg += f"\n\nExample questions for style reference:\n" + "\n".join(examples)

        question = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=600,
            messages=[{"role": "user", "content": f"{system}\n\n{user_msg}"}],
            response_model=Question,
        )
        return question

    except Exception as exc:
        logger.error("LLM generation failed: %s", exc)
        return _stub_question(language, cefr_level, skill_tag)


def generate_questions_batch(
    language: str,
    cefr_level: str,
    skill_tag: str,
    count: int = 5,
) -> list[Question]:
    return [generate_question(language, cefr_level, skill_tag) for _ in range(count)]


# --- Stub for offline / no-key development ---

from ..irt.priors import CEFR_TO_DIFFICULTY

_STUB_DATA: dict[str, dict] = {
    "spanish": {
        "past_tense": {
            "A2": {
                "question": "Which sentence uses the Spanish preterite tense correctly?",
                "options": [
                    "Yo como una manzana ayer.",
                    "Yo comí una manzana ayer.",
                    "Yo comeré una manzana ayer.",
                    "Yo comía una manzana ayer.",
                ],
                "correct_index": 1,
                "explanation": "The preterite tense (comí) is used for completed actions in the past. 'Ayer' (yesterday) signals a completed event.",
            }
        }
    }
}


def _stub_question(language: str, cefr_level: str, skill_tag: str) -> Question:
    stub = (
        _STUB_DATA.get(language, {})
        .get(skill_tag, {})
        .get(cefr_level, None)
    )
    if stub:
        return Question(
            **stub,
            cefr_level=cefr_level,
            skill_tag=skill_tag,
            language=language,
            estimated_difficulty_b=CEFR_TO_DIFFICULTY.get(cefr_level, 0.0),
        )
    return Question(
        question=f"[{cefr_level}] {language.capitalize()} question on {skill_tag}: fill in the blank.",
        options=["Option A", "Option B", "Option C", "Option D"],
        correct_index=0,
        explanation="This is a placeholder question. Add ANTHROPIC_API_KEY to generate real questions.",
        cefr_level=cefr_level,
        skill_tag=skill_tag,
        language=language,
        estimated_difficulty_b=CEFR_TO_DIFFICULTY.get(cefr_level, 0.0),
    )
