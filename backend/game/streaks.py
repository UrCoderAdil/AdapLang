"""Streak tracking and freeze item logic."""
from datetime import date, timedelta

STREAK_MILESTONES = {7, 30, 100, 365}


def compute_streak_update(
    current_streak: int,
    last_active_date: date | None,
    today: date | None = None,
    freeze_available: bool = False,
) -> dict:
    """
    Compute the new streak after a session on `today`.
    Returns:
        streak       — new streak count
        status       — 'extended' | 'started' | 'already_counted' | 'reset'
        milestone    — True if a milestone was hit
        freeze_used  — True if a freeze item was consumed
    """
    today = today or date.today()

    if last_active_date == today:
        return {"streak": current_streak, "status": "already_counted", "milestone": False, "freeze_used": False}

    yesterday = today - timedelta(days=1)
    two_days_ago = today - timedelta(days=2)

    if last_active_date == yesterday:
        new_streak = current_streak + 1
        status = "extended"
        freeze_used = False
    elif freeze_available and last_active_date == two_days_ago:
        new_streak = current_streak + 1
        status = "extended"
        freeze_used = True
    elif last_active_date is None:
        new_streak = 1
        status = "started"
        freeze_used = False
    else:
        new_streak = 1
        status = "reset"
        freeze_used = False

    return {
        "streak": new_streak,
        "status": status,
        "milestone": new_streak in STREAK_MILESTONES,
        "freeze_used": freeze_used,
    }
