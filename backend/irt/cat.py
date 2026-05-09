"""
Computerized Adaptive Testing helpers.
Wraps IRTModel.select_next_question with seen-question filtering.
"""
from .model import IRTModel


def select_cat_question(
    theta: float,
    question_pool: list[dict],
    seen_ids: set[str],
    sigma: float = 1.0,
) -> dict | None:
    """
    Pick the next question from the pool, excluding already-seen questions.
    Falls back to closest-b question if Fisher Information is degenerate.
    """
    available = [q for q in question_pool if q.get("id") not in seen_ids]
    if not available:
        return None

    model = IRTModel(theta=theta, sigma=sigma)
    return model.select_next_question(available)


def estimate_theta_from_scratch(responses: list[dict]) -> float:
    """Convenience: compute theta from a clean list of responses."""
    model = IRTModel()
    return model.update_theta(responses)
