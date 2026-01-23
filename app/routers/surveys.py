from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.db import get_connection

router = APIRouter(tags=["Surveys"])


# Models

class SurveyCreate(BaseModel):
    title: str

class QuestionCreate(BaseModel):
    questions: List[str]

# -------------------------
# APIs


@router.post("/surveys")
def create_survey(payload: SurveyCreate):
    conn = get_connection()
    cursor = conn.cursor()

    query = "INSERT INTO surveys (title, is_active) VALUES (%s, %s)"
    cursor.execute(query, (payload.title, False))
    conn.commit()

    survey_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return {
        "id": survey_id,
        "title": payload.title,
        "is_active": False
    }


@router.post("/surveys/{survey_id}/questions")
def add_questions(survey_id: int, payload: QuestionCreate):
    if len(payload.questions) != 5:
        raise HTTPException(status_code=400, detail="Exactly 5 questions required")

    conn = get_connection()
    cursor = conn.cursor()

    # Check survey exists
    cursor.execute("SELECT id FROM surveys WHERE id = %s", (survey_id,))
    if cursor.fetchone() is None:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Survey not found")

    # Insert questions
    for idx, q in enumerate(payload.questions, start=1):
        cursor.execute(
            "INSERT INTO survey_questions (survey_id, question_text, question_order) VALUES (%s, %s, %s)",
            (survey_id, q, idx)
        )

    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "5 questions added successfully"}

@router.post("/surveys/{survey_id}/publish")
def publish_survey(survey_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM surveys WHERE id = %s", (survey_id,))
    if cursor.fetchone() is None:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Survey not found")

    cursor.execute("UPDATE surveys SET is_active = TRUE WHERE id = %s", (survey_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Survey published successfully"}
