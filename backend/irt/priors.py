"""CEFR cold-start priors — map declared level to initial theta."""

CEFR_TO_THETA: dict[str, float] = {
    "A1": -2.5,
    "A2": -1.5,
    "B1": -0.5,
    "B2": 0.5,
    "C1": 1.5,
    "C2": 2.5,
}

CEFR_TO_DIFFICULTY: dict[str, float] = CEFR_TO_THETA  # question b uses same scale

CEFR_LEVELS = list(CEFR_TO_THETA.keys())


def theta_from_cefr(cefr_level: str) -> float:
    return CEFR_TO_THETA.get(cefr_level.upper(), 0.0)


def cefr_from_theta(theta: float) -> str:
    """Map a theta estimate back to the closest CEFR label."""
    closest = min(CEFR_TO_THETA, key=lambda k: abs(CEFR_TO_THETA[k] - theta))
    return closest
