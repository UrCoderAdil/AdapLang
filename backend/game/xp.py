"""XP award logic and logarithmic leveling curve."""
import math

XP_TABLE: dict[str, int] = {
    "correct_easy":   10,
    "correct_medium": 20,
    "correct_hard":   35,
    "correct_boss":   100,
    "streak_bonus":   5,
    "speed_crit":     15,
}


def xp_to_level(xp: int) -> int:
    """Logarithmic leveling — fast early, slower later."""
    if xp <= 0:
        return 1
    return max(1, int(math.log(1 + xp / 100, 1.5)))


def level_to_xp_required(level: int) -> int:
    """XP needed to *reach* the given level from level 0."""
    return int(100 * (1.5 ** level - 1))


def award_xp(
    is_correct: bool,
    question_b: float,
    user_theta: float,
    streak: int,
    response_time_ms: int,
    is_boss_question: bool = False,
) -> int:
    """Calculate total XP to award for a single question response."""
    if not is_correct:
        return 0

    if is_boss_question:
        base = XP_TABLE["correct_boss"]
    elif question_b >= user_theta + 0.5:
        base = XP_TABLE["correct_hard"]
    elif question_b >= user_theta - 0.5:
        base = XP_TABLE["correct_medium"]
    else:
        base = XP_TABLE["correct_easy"]

    bonus = 0
    if response_time_ms < 5_000:
        bonus += XP_TABLE["speed_crit"]
    if streak > 0:
        bonus += min(streak, 30) * XP_TABLE["streak_bonus"]

    return base + bonus


def xp_progress(current_xp: int) -> dict:
    """Return current level, XP in current level, and XP needed for next level."""
    level = xp_to_level(current_xp)
    xp_this_level = level_to_xp_required(level)
    xp_next_level = level_to_xp_required(level + 1)
    return {
        "level": level,
        "xp_in_level": current_xp - xp_this_level,
        "xp_needed": xp_next_level - xp_this_level,
        "total_xp": current_xp,
    }
