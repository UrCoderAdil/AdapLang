"""IRT admin endpoints — trigger recalibration, inspect theta."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...db import get_db, UserSkillState, Response as ResponseModel, Question as QuestionModel
from ...irt.model import IRTModel
from ...irt.priors import cefr_from_theta

router = APIRouter(prefix="/irt", tags=["irt"])


class ThetaResponse(BaseModel):
    user_id: str
    skill_tag: str
    theta: float
    cefr_estimate: str
    sigma: float


@router.get("/{user_id}/{skill_tag}", response_model=ThetaResponse)
def get_theta(user_id: str, skill_tag: str, db: Session = Depends(get_db)):
    state = (
        db.query(UserSkillState)
        .filter(UserSkillState.user_id == user_id, UserSkillState.skill_tag == skill_tag)
        .first()
    )
    if not state:
        raise HTTPException(status_code=404, detail="Skill state not found")
    return ThetaResponse(
        user_id=user_id,
        skill_tag=skill_tag,
        theta=round(state.theta, 3),
        cefr_estimate=cefr_from_theta(state.theta),
        sigma=round(state.sigma, 3),
    )


@router.post("/{user_id}/{skill_tag}/recalibrate")
def recalibrate_theta(user_id: str, skill_tag: str, db: Session = Depends(get_db)):
    """Recompute theta from all stored responses for this user+skill."""
    responses = (
        db.query(ResponseModel)
        .join(QuestionModel, ResponseModel.question_id == QuestionModel.id)
        .filter(ResponseModel.user_id == user_id, QuestionModel.skill_tag == skill_tag)
        .order_by(ResponseModel.created_at.asc())
        .all()
    )
    if not responses:
        raise HTTPException(status_code=404, detail="No responses found for recalibration")

    history = [{"b": r.question.b, "a": r.question.a, "c": r.question.c, "correct": r.correct} for r in responses]
    model = IRTModel()
    new_theta = model.update_theta(history)

    state = (
        db.query(UserSkillState)
        .filter(UserSkillState.user_id == user_id, UserSkillState.skill_tag == skill_tag)
        .first()
    )
    if state:
        state.theta = new_theta
        db.commit()

    return {"user_id": user_id, "skill_tag": skill_tag, "new_theta": round(new_theta, 3)}
