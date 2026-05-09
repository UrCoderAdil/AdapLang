"""
Offline IRT calibration script.
Run after accumulating 500+ responses per question.

Usage:
    python ml/calibrate_irt.py --db-url postgresql://... --output calibrated_items.json
"""
import argparse
import json
import logging
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_responses_from_db(db_url: str) -> tuple[list[str], list[str], np.ndarray]:
    from sqlalchemy import create_engine, text

    engine = create_engine(db_url)
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT user_id, question_id, correct FROM responses ORDER BY created_at")
        ).fetchall()

    user_ids = sorted(set(r[0] for r in rows))
    question_ids = sorted(set(r[1] for r in rows))

    uid_idx = {u: i for i, u in enumerate(user_ids)}
    qid_idx = {q: j for j, q in enumerate(question_ids)}

    matrix = np.full((len(user_ids), len(question_ids)), np.nan)
    for user_id, question_id, correct in rows:
        matrix[uid_idx[user_id], qid_idx[question_id]] = 1.0 if correct else 0.0

    return user_ids, question_ids, matrix


def filter_min_responses(matrix: np.ndarray, question_ids: list[str], min_responses: int = 50) -> tuple[list[str], np.ndarray]:
    counts = np.sum(~np.isnan(matrix), axis=0)
    keep = counts >= min_responses
    logger.info("Keeping %d / %d questions with >= %d responses", keep.sum(), len(question_ids), min_responses)
    return [q for q, k in zip(question_ids, keep) if k], matrix[:, keep]


def run_calibration(db_url: str, output_path: str, min_responses: int = 50):
    from backend.irt.calibration import calibrate_2pl

    logger.info("Loading responses from DB...")
    user_ids, question_ids, matrix = load_responses_from_db(db_url)
    logger.info("Loaded %d users × %d questions", len(user_ids), len(question_ids))

    question_ids, matrix = filter_min_responses(matrix, question_ids, min_responses)

    logger.info("Running 2PL MML calibration...")
    difficulty, discrimination = calibrate_2pl(matrix)

    results = {
        qid: {"b": float(b), "a": float(a)}
        for qid, b, a in zip(question_ids, difficulty, discrimination)
    }

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info("Saved calibrated parameters for %d questions to %s", len(results), output_path)
    return results


def apply_calibration_to_db(calibration: dict, db_url: str):
    """Update question b and a parameters in the DB from calibration results."""
    from sqlalchemy import create_engine, text

    engine = create_engine(db_url)
    with engine.connect() as conn:
        for qid, params in calibration.items():
            conn.execute(
                text("UPDATE questions SET b = :b, a = :a WHERE id = :id"),
                {"b": params["b"], "a": params["a"], "id": qid},
            )
        conn.commit()
    logger.info("Applied calibrated parameters to %d questions in DB.", len(calibration))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Offline IRT calibration")
    parser.add_argument("--db-url", default=os.getenv("DATABASE_URL"), required=False)
    parser.add_argument("--output", default="calibrated_items.json")
    parser.add_argument("--min-responses", type=int, default=50)
    parser.add_argument("--apply", action="store_true", help="Apply results back to DB")
    args = parser.parse_args()

    if not args.db_url:
        logger.error("DATABASE_URL not set. Pass --db-url or set the env var.")
        sys.exit(1)

    calibration = run_calibration(args.db_url, args.output, args.min_responses)
    if args.apply:
        apply_calibration_to_db(calibration, args.db_url)
