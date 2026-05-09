"""Game meta-endpoints: worlds, leaderboard, achievements."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...db import get_db, User
from ...game.battle import WORLDS, check_world_unlock
from ...game.achievements import ACHIEVEMENTS

router = APIRouter(prefix="/game", tags=["game"])


@router.get("/worlds")
def list_worlds():
    return {"worlds": WORLDS}


@router.get("/worlds/{user_id}/unlocked")
def unlocked_worlds(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")

    skill_states = user.skill_states
    theta = max((ss.theta for ss in skill_states), default=0.0)
    beaten = user.beaten_worlds or []

    newly_unlocked = check_world_unlock(theta, user.streak, beaten)
    all_unlocked = list(set(beaten) | set(newly_unlocked))

    if newly_unlocked:
        user.beaten_worlds = all_unlocked
        db.commit()

    return {"unlocked_world_ids": all_unlocked, "newly_unlocked": newly_unlocked}


@router.get("/leaderboard")
def leaderboard(db: Session = Depends(get_db), period: str = "all_time", limit: int = 20):
    users = (
        db.query(User)
        .order_by(User.total_xp.desc())
        .limit(limit)
        .all()
    )
    return {
        "period": period,
        "leaderboard": [
            {
                "rank": i + 1,
                "user_id": u.id,
                "display_name": u.display_name or "Anonymous",
                "level": u.level,
                "total_xp": u.total_xp,
                "streak": u.streak,
            }
            for i, u in enumerate(users)
        ],
    }


@router.get("/achievements")
def list_achievements():
    return {"achievements": ACHIEVEMENTS}
