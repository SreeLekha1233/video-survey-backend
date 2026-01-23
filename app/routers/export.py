from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.db import get_connection
import os
import json
import zipfile
import uuid
from datetime import datetime

router = APIRouter(tags=["Export"])

@router.get("/submissions/{submission_id}/export")
def export_submission(submission_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Check submission exists
    cursor.execute("SELECT * FROM survey_submissions WHERE id = %s", (submission_id,))
    submission = cursor.fetchone()
    if not submission:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Submission not found")

    # Get answers
    cursor.execute("""
        SELECT sa.*, sq.question_text
        FROM survey_answers sa
        JOIN survey_questions sq ON sa.question_id = sq.id
        WHERE sa.submission_id = %s
        ORDER BY sq.question_order
    """, (submission_id,))
    answers = cursor.fetchall()

    # Get media files
    cursor.execute("SELECT * FROM media_files WHERE submission_id = %s", (submission_id,))
    media_files = cursor.fetchall()

    cursor.close()
    conn.close()

    # Build metadata.json
    metadata = {
        "submission_id": submission["id"],
        "survey_id": submission["survey_id"],
        "started_at": str(submission["started_at"]),
        "completed_at": str(submission["completed_at"]),
        "ip_address": submission["ip_address"],
        "device": submission["device"],
        "browser": submission["browser"],
        "os": submission["os"],
        "location": submission["location"],
        "overall_score": submission["overall_score"],
        "responses": []
    }

    for a in answers:
        metadata["responses"].append({
            "question": a["question_text"],
            "answer": a["answer"],
            "face_detected": bool(a["face_detected"]),
            "score": a["face_score"],
            "face_image": a["face_image_path"]
        })

    # Create temp zip
    export_folder = "exports"
    os.makedirs(export_folder, exist_ok=True)

    zip_name = f"submission_{submission_id}_{uuid.uuid4().hex}.zip"
    zip_path = os.path.join(export_folder, zip_name)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Add metadata.json
        metadata_path = os.path.join(export_folder, f"metadata_{submission_id}.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        zipf.write(metadata_path, arcname="metadata.json")

        # Add media files
        for m in media_files:
            if os.path.exists(m["path"]):
                if m["type"] == "image":
                    arcname = f"images/{os.path.basename(m['path'])}"
                else:
                    arcname = f"videos/{os.path.basename(m['path'])}"

                zipf.write(m["path"], arcname=arcname)

    return FileResponse(zip_path, filename=f"submission_{submission_id}.zip")
