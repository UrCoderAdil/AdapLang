"""User profile, registration, and streak endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...db import get_db, User, UserSkillState, UserQuestionState
from ...db.models import Response as ResponseModel
from ...game.xp import xp_progress
from ...irt.priors import theta_from_cefr, cefr_from_theta
from ...srs.scheduler import get_due_question_ids

router = APIRouter(prefix="/user", tags=["user"])


class UserCreateRequest(BaseModel):
    email: str
    display_name: str | None = None
    starting_cefr: str = "A1"
    language: str = "spanish"


class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str | None
    streak: int
    level: int
    total_xp: int
    current_world: int
    achievements: list[str]


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(payload: UserCreateRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(email=payload.email, display_name=payload.display_name)
    db.add(user)
    db.flush()

    initial_theta = theta_from_cefr(payload.starting_cefr)
    skill_state = UserSkillState(
        user_id=user.id,
        skill_tag=payload.language,
        theta=initial_theta,
        sigma=1.0,
    )
    db.add(skill_state)
    db.commit()
    db.refresh(user)

    return _user_response(user)


@router.get("/{user_id}/profile", response_model=UserResponse)
def get_profile(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _user_response(user)


@router.get("/{user_id}/stats")
def get_stats(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    skill_states = db.query(UserSkillState).filter(UserSkillState.user_id == user_id).all()
    skills = {
        ss.skill_tag: {
            "theta": round(ss.theta, 3),
            "cefr": cefr_from_theta(ss.theta),
        }
        for ss in skill_states
    }

    total_responses = db.query(ResponseModel).filter(ResponseModel.user_id == user_id).count()
    correct_responses = db.query(ResponseModel).filter(
        ResponseModel.user_id == user_id, ResponseModel.correct == True
    ).count()

    return {
        **_user_response(user).model_dump(),
        "skills": skills,
        "xp_progress": xp_progress(user.total_xp),
        "total_questions_answered": total_responses,
        "accuracy": round(correct_responses / max(total_responses, 1), 3),
    }


@router.get("/{user_id}/review")
def get_due_reviews(user_id: str, db: Session = Depends(get_db), limit: int = 20):
    """Return question IDs due for spaced repetition review today."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    states = (
        db.query(UserQuestionState)
        .filter(UserQuestionState.user_id == user_id)
        .all()
    )
    state_dicts = [
        {"question_id": s.question_id, "next_review_at": s.next_review_at}
        for s in states
    ]
    due_ids = get_due_question_ids(state_dicts, limit=limit)
    return {"due_question_ids": due_ids, "count": len(due_ids)}


def _user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        streak=user.streak,
        level=user.level,
        total_xp=user.total_xp,
        current_world=user.current_world,
        achievements=user.achievement_ids or [],
    )
