"""
Prepare fine-tuning dataset for Mistral-7B.

Sources:
  1. Your own manually verified questions (export from DB)
  2. Filtered LLM-generated questions (quality_score >= 8)
  3. (Optional) Duolingo SLAM dataset reformatted

Output: data/finetune_dataset.jsonl (one JSON object per line)
"""
import json
import os
import sys
import argparse
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert language teacher and psychometrician. "
    "Generate high-quality multiple-choice language learning questions. "
    "Output only valid JSON matching the provided schema."
)


def format_for_finetune(question: dict) -> dict:
    """Format a question dict into a chat-style training example."""
    user_msg = (
        f"Generate a {question['cefr_level']} {question['language']} "
        f"question on the skill: {question['skill_tag']}."
    )
    assistant_msg = json.dumps(
        {
            "question": question["question"],
            "options": question["options"],
            "correct_index": question["correct_index"],
            "explanation": question["explanation"],
            "cefr_level": question["cefr_level"],
            "skill_tag": question["skill_tag"],
            "language": question["language"],
            "estimated_difficulty_b": question.get("b", 0.0),
        },
        ensure_ascii=False,
    )
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": assistant_msg},
        ]
    }


def load_from_db(db_url: str, min_quality: float = 8.0) -> list[dict]:
    from sqlalchemy import create_engine, text

    engine = create_engine(db_url)
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT question, options, correct_index, explanation, "
                "cefr_level, skill_tag, language, b, quality_score "
                "FROM questions WHERE quality_score >= :min_q"
            ),
            {"min_q": min_quality},
        ).fetchall()

    questions = []
    for r in rows:
        questions.append(
            {
                "question": r[0],
                "options": r[1],
                "correct_index": r[2],
                "explanation": r[3],
                "cefr_level": r[4],
                "skill_tag": r[5],
                "language": r[6],
                "b": r[7],
            }
        )
    logger.info("Loaded %d high-quality questions from DB.", len(questions))
    return questions


def write_dataset(examples: list[dict], output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    logger.info("Wrote %d training examples to %s", len(examples), output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-url", default=os.getenv("DATABASE_URL"))
    parser.add_argument("--output", default="data/finetune_dataset.jsonl")
    parser.add_argument("--min-quality", type=float, default=8.0)
    args = parser.parse_args()

    if not args.db_url:
        logger.error("DATABASE_URL not set.")
        sys.exit(1)

    questions = load_from_db(args.db_url, args.min_quality)
    examples = [format_for_finetune(q) for q in questions]
    write_dataset(examples, args.output)
