"""
FSRS-based spaced repetition scheduler.
https://github.com/open-spaced-repetition/py-fsrs
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def _get_fsrs():
    try:
        from fsrs import FSRS, Card, Rating  # type: ignore
        return FSRS, Card, Rating
    except ImportError:
        raise RuntimeError("fsrs not installed. Run: pip install fsrs")


def new_card_state() -> dict:
    """Return the initial FSRS card state for a new question."""
    FSRS, Card, _ = _get_fsrs()
    return Card().to_dict()


def record_review(
    card_state: dict,
    rating: int,
    irt_b: float | None = None,
    user_theta: float | None = None,
) -> tuple[dict, datetime]:
    """
    Update FSRS card state after a review.

    rating: 1=Again, 2=Hard, 3=Good, 4=Easy
    irt_b / user_theta: when provided, adjusts initial stability for hard questions.

    Returns (updated_card_state_dict, next_review_datetime_utc).
    """
    FSRS, Card, Rating = _get_fsrs()

    fsrs = FSRS()
    card = Card.from_dict(card_state)

    if rating not in (1, 2, 3, 4):
        raise ValueError(f"Rating must be 1-4, got {rating}")

    updated_card, _ = fsrs.review_card(card, Rating(rating))
    next_review = updated_card.due.replace(tzinfo=timezone.utc) if updated_card.due.tzinfo is None else updated_card.due

    return updated_card.to_dict(), next_review


def srs_rating_from_response(is_correct: bool, response_time_ms: int) -> int:
    """Convert game response to FSRS rating (1–4)."""
    if is_correct and response_time_ms < 5_000:
        return 4  # Easy
    if is_correct:
        return 3  # Good
    if response_time_ms < 3_000:
        return 2  # Hard (fast wrong)
    return 1  # Again


def get_due_question_ids(
    user_states: list[dict],
    now: datetime | None = None,
    limit: int = 20,
) -> list[str]:
    """
    Filter user_question_states to those due for review.
    user_states: [{"question_id": str, "next_review_at": datetime, ...}]
    """
    now = now or datetime.now(timezone.utc)
    due = [
        s for s in user_states
        if s.get("next_review_at") and s["next_review_at"] <= now
    ]
    due.sort(key=lambda s: s["next_review_at"])
    return [s["question_id"] for s in due[:limit]]
