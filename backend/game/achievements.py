"""Achievement / badge unlock system."""
from __future__ import annotations

ACHIEVEMENTS: list[dict] = [
    {"id": "first_correct",    "name": "First Blood",      "desc": "Answer your first question correctly."},
    {"id": "streak_7",         "name": "Week Warrior",     "desc": "Maintain a 7-day streak."},
    {"id": "streak_30",        "name": "Iron Learner",     "desc": "Maintain a 30-day streak."},
    {"id": "streak_100",       "name": "Century Scholar",  "desc": "Maintain a 100-day streak."},
    {"id": "level_10",         "name": "Apprentice",       "desc": "Reach level 10."},
    {"id": "level_25",         "name": "Journeyman",       "desc": "Reach level 25."},
    {"id": "level_50",         "name": "Adept",            "desc": "Reach level 50."},
    {"id": "boss_1",           "name": "Forest Slayer",    "desc": "Defeat the Forest of Greetings boss."},
    {"id": "boss_2",           "name": "Cave Conqueror",   "desc": "Defeat the Caves of Past Tense boss."},
    {"id": "boss_5",           "name": "Tower Master",     "desc": "Defeat the Ancient Tower boss."},
    {"id": "theta_b2",         "name": "B2 Achiever",      "desc": "Reach B2 skill level (θ ≥ 0.5)."},
    {"id": "theta_c1",         "name": "C1 Elite",         "desc": "Reach C1 skill level (θ ≥ 1.5)."},
    {"id": "speed_demon",      "name": "Speed Demon",      "desc": "Answer 10 questions correctly in under 3 s each."},
    {"id": "perfect_session",  "name": "Perfect Session",  "desc": "Complete a full battle session with no mistakes."},
]

_ACHIEVEMENT_MAP = {a["id"]: a for a in ACHIEVEMENTS}


def check_achievements(
    user_stats: dict,
    existing_achievement_ids: set[str],
) -> list[dict]:
    """
    Return list of newly unlocked achievement dicts.

    user_stats keys: streak, level, theta, beaten_worlds, total_correct,
                     fast_correct_streak, session_errors
    """
    unlocked: list[dict] = []

    def unlock(aid: str):
        if aid not in existing_achievement_ids:
            unlocked.append(_ACHIEVEMENT_MAP[aid])

    if user_stats.get("total_correct", 0) >= 1:
        unlock("first_correct")
    if user_stats.get("streak", 0) >= 7:
        unlock("streak_7")
    if user_stats.get("streak", 0) >= 30:
        unlock("streak_30")
    if user_stats.get("streak", 0) >= 100:
        unlock("streak_100")
    if user_stats.get("level", 0) >= 10:
        unlock("level_10")
    if user_stats.get("level", 0) >= 25:
        unlock("level_25")
    if user_stats.get("level", 0) >= 50:
        unlock("level_50")
    beaten = set(user_stats.get("beaten_worlds", []))
    for i in [1, 2, 5]:
        if i in beaten:
            unlock(f"boss_{i}")
    if user_stats.get("theta", -999) >= 0.5:
        unlock("theta_b2")
    if user_stats.get("theta", -999) >= 1.5:
        unlock("theta_c1")
    if user_stats.get("fast_correct_streak", 0) >= 10:
        unlock("speed_demon")
    if user_stats.get("session_errors", 1) == 0:
        unlock("perfect_session")

    return unlocked
