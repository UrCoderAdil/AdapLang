"""
Generate and seed questions via LLM.
Usage: python -m quiz_gen.seed_questions --language spanish --count 50
"""
import argparse
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SKILL_TAGS_BY_CEFR = {
    "A1": ["greetings", "numbers", "colors", "days_of_week", "basic_verbs"],
    "A2": ["past_tense", "present_continuous", "family_vocabulary", "shopping", "directions"],
    "B1": ["subjunctive", "conditionals", "vocabulary_food", "idioms", "phrasal_verbs"],
    "B2": ["ser_vs_estar", "advanced_grammar", "formal_writing", "literature", "debate"],
    "C1": ["nuanced_vocabulary", "register_shifts", "complex_syntax", "rhetoric", "etymology"],
    "C2": ["idiomatic_mastery", "literary_analysis", "pragmatics", "cultural_references", "collocations"],
}


def seed(language: str, count: int, min_quality: float = 7.0):
    from backend.quiz_gen.generator import generate_question
    from backend.quiz_gen.quality_filter import passes_quality_bar
    from backend.db.database import SessionLocal, create_tables
    from backend.db.models import Question as QuestionModel
    from backend.irt.priors import CEFR_TO_DIFFICULTY

    cefr_levels = list(SKILL_TAGS_BY_CEFR.keys())
    create_tables()
    db = SessionLocal()
    generated = 0
    attempts = 0

    try:
        while generated < count and attempts < count * 3:
            cefr = cefr_levels[attempts % len(cefr_levels)]
            skills = SKILL_TAGS_BY_CEFR[cefr]
            skill_tag = skills[attempts % len(skills)]
            attempts += 1

            q = generate_question(language, cefr, skill_tag)
            passed, score_result = passes_quality_bar(q)
            logger.info(
                "[%s/%s] %s | quality=%.1f | pass=%s",
                cefr, skill_tag, q.question[:40], score_result.score, passed
            )
            if not passed:
                continue

            row = QuestionModel(
                language=q.language,
                cefr_level=q.cefr_level,
                skill_tag=q.skill_tag,
                question=q.question,
                options=q.options,
                correct_index=q.correct_index,
                explanation=q.explanation,
                b=q.estimated_difficulty_b,
                a=1.0,
                c=0.25,
                quality_score=score_result.score,
                world_id=cefr_levels.index(cefr) + 1,
            )
            db.add(row)
            db.commit()
            generated += 1
            logger.info("Saved question %d / %d", generated, count)
    finally:
        db.close()

    logger.info("Done. Generated %d questions in %d attempts.", generated, attempts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", default="spanish")
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument("--min-quality", type=float, default=7.0)
    args = parser.parse_args()
    seed(args.language, args.count, args.min_quality)
