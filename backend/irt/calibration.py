"""
Offline IRT item calibration.
Run after collecting 500+ responses per question.
Uses the `girth` library for 2PL/3PL MML estimation.
"""
import numpy as np


def calibrate_2pl(response_matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Estimate (difficulty, discrimination) for each question via MML.

    response_matrix: shape (n_users, n_questions)
        Values: 1 = correct, 0 = wrong, np.nan = not attempted
    Returns:
        difficulty   (n_questions,)
        discrimination (n_questions,)
    """
    try:
        from girth import twopl_mml  # type: ignore

        difficulty, discrimination = twopl_mml(response_matrix)
        return difficulty, discrimination
    except ImportError:
        raise RuntimeError(
            "girth is not installed. Run: pip install girth"
        )


def build_response_matrix(
    responses: list[dict],
    user_ids: list[str],
    question_ids: list[str],
) -> np.ndarray:
    """
    Convert a flat list of response dicts into a (users × questions) matrix.
    responses: [{"user_id": str, "question_id": str, "correct": bool}, ...]
    """
    uid_idx = {uid: i for i, uid in enumerate(user_ids)}
    qid_idx = {qid: j for j, qid in enumerate(question_ids)}

    matrix = np.full((len(user_ids), len(question_ids)), np.nan)
    for r in responses:
        i = uid_idx.get(r["user_id"])
        j = qid_idx.get(r["question_id"])
        if i is not None and j is not None:
            matrix[i, j] = 1.0 if r["correct"] else 0.0
    return matrix
