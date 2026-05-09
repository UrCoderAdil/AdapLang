"""Quiz session endpoints — the core adaptive game loop."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...db import get_db, Question as QuestionModel, Response as ResponseModel, User, UserSkillState, UserQuestionState
from ...irt.model import IRTModel
from ...irt.cat import select_cat_question
from ...game.battle import calculate_damage
from ...game.xp import award_xp, xp_progress, xp_to_level
from ...game.streaks import compute_streak_update
from ...game.achievements import check_achievements
from ...srs.scheduler import record_review as srs_record_review, srs_rating_from_response, new_card_state

router = APIRouter(prefix="/session", tags=["session"])


class SessionStartRequest(BaseModel):
    user_id: str
    world_id: int = 1
    language: str = "spanish"


class SessionStartResponse(BaseModel):
    session_id: str
    question: dict
    boss_hp: int
    player_hp: int


class AnswerPayload(BaseModel):
    session_id: str
    user_id: str
    question_id: str
    selected_index: int
    response_time_ms: int


@router.post("/start", response_model=SessionStartResponse)
def start_session(payload: SessionStartRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    skill_state = (
        db.query(UserSkillState)
        .filter(UserSkillState.user_id == payload.user_id, UserSkillState.skill_tag == payload.language)
        .first()
    )
    theta = skill_state.theta if skill_state else 0.0

    pool = (
        db.query(QuestionModel)
        .filter(QuestionModel.world_id == payload.world_id, QuestionModel.language == payload.language)
        .limit(50)
        .all()
    )
    if not pool:
        pool = db.query(QuestionModel).filter(QuestionModel.language == payload.language).limit(50).all()

    pool_dicts = [_question_to_dict(q) for q in pool]
    model = IRTModel(theta=theta)
    next_q = model.select_next_question(pool_dicts) or (pool_dicts[0] if pool_dicts else None)
    if not next_q:
        raise HTTPException(status_code=404, detail="No questions available")

    from ...game.battle import scale_boss_hp
    boss_hp = scale_boss_hp(theta, payload.world_id)

    return SessionStartResponse(
        session_id=str(uuid.uuid4()),
        question=_sanitize_question(next_q),
        boss_hp=boss_hp,
        player_hp=100,
    )


@router.post("/answer")
def submit_answer(payload: AnswerPayload, db: Session = Depends(get_db)):
    question = db.query(QuestionModel).filter(QuestionModel.id == payload.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    skill_tag = question.skill_tag
    skill_state = (
        db.query(UserSkillState)
        .filter(UserSkillState.user_id == payload.user_id, UserSkillState.skill_tag == skill_tag)
        .first()
    )
    if not skill_state:
        skill_state = UserSkillState(user_id=payload.user_id, skill_tag=skill_tag, theta=0.0, sigma=1.0)
        db.add(skill_state)

    is_correct = payload.selected_index == question.correct_index

    # IRT update
    recent_responses = (
        db.query(ResponseModel)
        .join(QuestionModel, ResponseModel.question_id == QuestionModel.id)
        .filter(ResponseModel.user_id == payload.user_id, QuestionModel.skill_tag == skill_tag)
        .order_by(ResponseModel.created_at.desc())
        .limit(20)
        .all()
    )
    history = [
        {"b": r.question.b, "a": r.question.a, "c": r.question.c, "correct": r.correct}
        for r in recent_responses
    ]
    history.append({"b": question.b, "a": question.a, "c": question.c, "correct": is_correct})

    irt_model = IRTModel(theta=skill_state.theta, sigma=skill_state.sigma)
    new_theta = irt_model.update_theta(history)
    skill_state.theta = new_theta

    # Log response
    response_row = ResponseModel(
        user_id=payload.user_id,
        question_id=payload.question_id,
        correct=is_correct,
        response_time_ms=payload.response_time_ms,
    )
    db.add(response_row)

    # SRS update
    uqs = (
        db.query(UserQuestionState)
        .filter(UserQuestionState.user_id == payload.user_id, UserQuestionState.question_id == payload.question_id)
        .first()
    )
    if not uqs:
        uqs = UserQuestionState(
            user_id=payload.user_id,
            question_id=payload.question_id,
            fsrs_card_state=new_card_state(),
        )
        db.add(uqs)
    try:
        srs_rating = srs_rating_from_response(is_correct, payload.response_time_ms)
        updated_state, next_review = srs_record_review(uqs.fsrs_card_state or new_card_state(), srs_rating)
        uqs.fsrs_card_state = updated_state
        uqs.next_review_at = next_review
    except Exception:
        pass

    # Battle
    battle_result = calculate_damage(is_correct, new_theta, question.b, payload.response_time_ms)

    # XP + streak
    import datetime as dt
    today = dt.date.today()
    streak_result = compute_streak_update(
        current_streak=user.streak,
        last_active_date=user.last_active_date,
        today=today,
        freeze_available=user.freeze_items > 0,
    )
    if streak_result["freeze_used"]:
        user.freeze_items = max(0, user.freeze_items - 1)
    user.streak = streak_result["streak"]
    user.last_active_date = today

    xp_gained = award_xp(
        is_correct=is_correct,
        question_b=question.b,
        user_theta=new_theta,
        streak=user.streak,
        response_time_ms=payload.response_time_ms,
        is_boss_question=question.is_boss_question or False,
    )
    user.total_xp += xp_gained
    user.level = xp_to_level(user.total_xp)

    # Achievements
    user_stats = {
        "streak": user.streak,
        "level": user.level,
        "theta": new_theta,
        "beaten_worlds": user.beaten_worlds or [],
        "total_correct": db.query(ResponseModel).filter(
            ResponseModel.user_id == payload.user_id, ResponseModel.correct == True
        ).count() + (1 if is_correct else 0),
        "session_errors": 0,
    }
    existing_aids = set(user.achievement_ids or [])
    new_achievements = check_achievements(user_stats, existing_aids)
    if new_achievements:
        user.achievement_ids = list(existing_aids | {a["id"] for a in new_achievements})

    # Next question via CAT
    seen_ids = {r.question_id for r in recent_responses} | {payload.question_id}
    pool = (
        db.query(QuestionModel)
        .filter(QuestionModel.skill_tag == skill_tag, QuestionModel.language == question.language)
        .limit(50)
        .all()
    )
    pool_dicts = [_question_to_dict(q) for q in pool]
    next_question = select_cat_question(new_theta, pool_dicts, seen_ids)

    db.commit()

    return {
        "correct": is_correct,
        "explanation": question.explanation,
        "battle_result": battle_result,
        "xp_gained": xp_gained,
        "xp_progress": xp_progress(user.total_xp),
        "streak": streak_result,
        "new_theta": round(new_theta, 3),
        "new_achievements": new_achievements,
        "next_question": _sanitize_question(next_question) if next_question else None,
    }


def _question_to_dict(q: QuestionModel) -> dict:
    return {
        "id": q.id,
        "question": q.question,
        "options": q.options,
        "correct_index": q.correct_index,
        "explanation": q.explanation,
        "cefr_level": q.cefr_level,
        "skill_tag": q.skill_tag,
        "language": q.language,
        "b": q.b,
        "a": q.a,
        "c": q.c,
        "is_boss_question": q.is_boss_question or False,
    }


def _sanitize_question(q: dict) -> dict:
    """Strip answer info before sending to client."""
    return {k: v for k, v in q.items() if k not in ("correct_index", "explanation", "b", "a", "c")}
