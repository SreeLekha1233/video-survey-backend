from fastapi import APIRouter, HTTPException, Request
from app.db import get_connection
from datetime import datetime
from fastapi import UploadFile, File
import os
import uuid


router = APIRouter(tags=["Submissions"])

@router.post("/surveys/{survey_id}/start")
def start_submission(survey_id: int, request: Request):
    conn = get_connection()
    cursor = conn.cursor()

    # Check survey exists and is active
    cursor.execute("SELECT id FROM surveys WHERE id = %s AND is_active = TRUE", (survey_id,))
    row = cursor.fetchone()
    if row is None:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Survey not found or not active")

    # Extract metadata
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    device = "Unknown"
    os = "Unknown"
    browser = user_agent[:100]  # simple version

    started_at = datetime.now()

    # Insert submission
    cursor.execute("""
        INSERT INTO survey_submissions
        (survey_id, ip_address, device, browser, os, location, started_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        survey_id,
        ip_address,
        device,
        browser,
        os,
        "Unknown",
        started_at
    ))

    conn.commit()
    submission_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return {"submission_id": submission_id}

from pydantic import BaseModel

# Request model
class AnswerCreate(BaseModel):
    question_id: int
    answer: str
    face_detected: bool
    face_score: int
    face_image_path: str


@router.post("/submissions/{submission_id}/answers")
def save_answer(submission_id: int, payload: AnswerCreate):
    conn = get_connection()
    cursor = conn.cursor()

    # Check submission exists
    cursor.execute("SELECT id FROM survey_submissions WHERE id = %s", (submission_id,))
    if cursor.fetchone() is None:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Submission not found")

    # Normalize answer
    answer = payload.answer.strip().capitalize()
    if answer not in ["Yes", "No"]:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Answer must be Yes or No")

    # Insert answer
    cursor.execute("""
        INSERT INTO survey_answers
        (submission_id, question_id, answer, face_detected, face_score, face_image_path)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        submission_id,
        payload.question_id,
        answer,
        payload.face_detected,
        payload.face_score,
        payload.face_image_path
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Answer saved successfully"}

@router.post("/submissions/{submission_id}/complete")
def complete_submission(submission_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    # Check submission exists
    cursor.execute("SELECT id FROM survey_submissions WHERE id = %s", (submission_id,))
    if cursor.fetchone() is None:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Submission not found")

    # Calculate average score
    cursor.execute("""
        SELECT AVG(face_score)
        FROM survey_answers
        WHERE submission_id = %s
    """, (submission_id,))
    avg_score = cursor.fetchone()[0]

    if avg_score is None:
        avg_score = 0

    from datetime import datetime
    completed_at = datetime.now()

    # Update submission
    cursor.execute("""
        UPDATE survey_submissions
        SET completed_at = %s, overall_score = %s
        WHERE id = %s
    """, (completed_at, int(avg_score), submission_id))

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "message": "Submission completed successfully",
        "overall_score": int(avg_score)
    }

@router.post("/submissions/{submission_id}/media")
def upload_media(submission_id: int, file: UploadFile = File(...)):
    conn = get_connection()
    cursor = conn.cursor()

    # Check submission exists
    cursor.execute("SELECT id FROM survey_submissions WHERE id = %s", (submission_id,))
    if cursor.fetchone() is None:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Submission not found")

    # Decide folder by file type
    filename = file.filename.lower()
    if filename.endswith(".mp4") or filename.endswith(".mov"):
        folder = "media/videos"
        media_type = "video"
    else:
        folder = "media/images"
        media_type = "image"

    # Create unique filename
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(folder, unique_name)

    # Save file to disk
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Save path in DB
    cursor.execute("""
        INSERT INTO media_files (submission_id, type, path)
        VALUES (%s, %s, %s)
    """, (submission_id, media_type, file_path))

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "message": "File uploaded successfully",
        "path": file_path
    }
