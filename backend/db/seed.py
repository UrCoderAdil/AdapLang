"""
Seed the database with an initial bank of questions.
Run: python -m db.seed
"""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from backend.db.database import SessionLocal, create_tables
from backend.db.models import Question
from backend.irt.priors import CEFR_TO_DIFFICULTY

SEED_QUESTIONS = [
    # Spanish — A1
    dict(language="spanish", cefr_level="A1", skill_tag="greetings",
         question="How do you say 'Good morning' in Spanish?",
         options=["Buenas noches", "Buenos días", "Buenas tardes", "Hola"],
         correct_index=1,
         explanation="'Buenos días' literally means 'Good days' and is used in the morning. 'Buenas noches' = good night, 'Buenas tardes' = good afternoon.",
         b=CEFR_TO_DIFFICULTY["A1"], a=1.0, c=0.25, quality_score=9.0),
    dict(language="spanish", cefr_level="A1", skill_tag="numbers",
         question="What is 'five' in Spanish?",
         options=["Cuatro", "Seis", "Cinco", "Tres"],
         correct_index=2,
         explanation="'Cinco' = 5. Remember: uno(1), dos(2), tres(3), cuatro(4), cinco(5).",
         b=CEFR_TO_DIFFICULTY["A1"], a=1.0, c=0.25, quality_score=8.5),
    # Spanish — A2
    dict(language="spanish", cefr_level="A2", skill_tag="past_tense",
         question="Which sentence uses the Spanish preterite tense correctly?",
         options=["Yo como una manzana ayer.", "Yo comí una manzana ayer.",
                  "Yo comeré una manzana ayer.", "Yo comía una manzana ayer."],
         correct_index=1,
         explanation="The preterite (comí) marks completed past actions. 'Ayer' (yesterday) confirms this is a single completed event, not a habit (imperfect) or future.",
         b=CEFR_TO_DIFFICULTY["A2"], a=1.2, c=0.25, quality_score=9.2),
    # Spanish — B1
    dict(language="spanish", cefr_level="B1", skill_tag="subjunctive",
         question="Choose the correct form: 'Quiero que tú ___ más.' (estudiar)",
         options=["estudias", "estudies", "estudiarás", "estudie"],
         correct_index=1,
         explanation="After 'querer que' + different subject, use present subjunctive. 'estudies' is the tú form of the subjunctive of estudiar.",
         b=CEFR_TO_DIFFICULTY["B1"], a=1.4, c=0.25, quality_score=9.5),
    # Spanish — B2
    dict(language="spanish", cefr_level="B2", skill_tag="ser_vs_estar",
         question="Which sentence is grammatically correct and natural?",
         options=[
             "La conferencia es en el auditorio mañana.",
             "La conferencia está en el auditorio mañana.",
             "La conferencia estuvo en el auditorio mañana.",
             "La conferencia era en el auditorio mañana.",
         ],
         correct_index=1,
         explanation="'Estar' is used for location of events in progress or scheduled. 'Es' can also work for scheduled events, but 'está' sounds more natural when the location is the focus.",
         b=CEFR_TO_DIFFICULTY["B2"], a=1.3, c=0.25, quality_score=8.8),
    # French — A1
    dict(language="french", cefr_level="A1", skill_tag="greetings",
         question="How do you say 'Thank you' in French?",
         options=["S'il vous plaît", "Merci", "Bonjour", "Au revoir"],
         correct_index=1,
         explanation="'Merci' means thank you. 'S'il vous plaît' = please, 'Bonjour' = hello, 'Au revoir' = goodbye.",
         b=CEFR_TO_DIFFICULTY["A1"], a=1.0, c=0.25, quality_score=9.0),
    # French — B1
    dict(language="french", cefr_level="B1", skill_tag="past_tense",
         question="'I have eaten' in French is:",
         options=["J'ai mangé", "Je mange", "J'avais mangé", "Je mangeais"],
         correct_index=0,
         explanation="'J'ai mangé' is passé composé (avoir + past participle) — used for completed actions in spoken French. 'Je mangeais' = imperfect (ongoing/habitual past).",
         b=CEFR_TO_DIFFICULTY["B1"], a=1.2, c=0.25, quality_score=9.1),
]


def run_seed():
    create_tables()
    db = SessionLocal()
    try:
        existing = db.query(Question).count()
        if existing >= len(SEED_QUESTIONS):
            print(f"DB already has {existing} questions — skipping seed.")
            return

        added = 0
        for q in SEED_QUESTIONS:
            row = Question(**q)
            db.add(row)
            added += 1

        db.commit()
        print(f"Seeded {added} questions.")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
