"""Battle mechanics: damage, boss HP scaling, combat outcomes."""
from __future__ import annotations

WORLDS: list[dict] = [
    {"id": 1, "name": "Forest of Greetings",   "topic": "A1 basics",       "unlock": "default",              "difficulty": -2.5},
    {"id": 2, "name": "Caves of Past Tense",   "topic": "A2 grammar",      "unlock": "defeat_world_1_boss",  "difficulty": -1.5},
    {"id": 3, "name": "City of Conversations", "topic": "B1 vocabulary",   "unlock": "streak_7_world_2",     "difficulty": -0.5},
    {"id": 4, "name": "Dragon's Subjunctive",  "topic": "B2 grammar",      "unlock": "theta_1.0",            "difficulty":  0.5},
    {"id": 5, "name": "Ancient Tower",         "topic": "C1/C2 mastery",   "unlock": "theta_2.0_streak_30",  "difficulty":  2.0},
]


def calculate_damage(
    is_correct: bool,
    theta: float,
    question_b: float,
    response_time_ms: int,
) -> dict:
    """
    Correct answer → damage to boss.
    Wrong answer   → damage to player.
    Speed bonus: answer in <5 s gives 1.5× multiplier.
    """
    base_damage = 20
    difficulty_bonus = max(0.0, (question_b - theta) * 10)
    speed_multiplier = 1.5 if response_time_ms < 5_000 else 1.0

    if is_correct:
        damage = int((base_damage + difficulty_bonus) * speed_multiplier)
        return {"target": "boss", "damage": damage, "crit": speed_multiplier > 1.0}
    else:
        return {"target": "player", "damage": base_damage // 2, "crit": False}


def scale_boss_hp(user_theta: float, world_level: int) -> int:
    """Boss HP scales with the gap between user skill and world difficulty."""
    world_difficulty = world_level * 0.5 - 2.5
    skill_gap = abs(world_difficulty - user_theta)
    base_hp = 200
    return int(base_hp * (1 + skill_gap * 0.3))


def check_world_unlock(user_theta: float, streak: int, beaten_worlds: list[int]) -> list[int]:
    """Return list of newly unlocked world IDs."""
    newly_unlocked: list[int] = []
    for world in WORLDS:
        wid = world["id"]
        if wid in beaten_worlds:
            continue
        unlock = world["unlock"]
        if unlock == "default":
            newly_unlocked.append(wid)
        elif unlock == "defeat_world_1_boss" and 1 in beaten_worlds:
            newly_unlocked.append(wid)
        elif unlock == "streak_7_world_2" and streak >= 7 and 2 in beaten_worlds:
            newly_unlocked.append(wid)
        elif unlock == "theta_1.0" and user_theta >= 1.0:
            newly_unlocked.append(wid)
        elif unlock == "theta_2.0_streak_30" and user_theta >= 2.0 and streak >= 30:
            newly_unlocked.append(wid)
    return newly_unlocked
