#  Video Survey Backend (FastAPI + MySQL)

This project is a backend system for a **privacy-first video survey platform** where users answer a 5-question Yes/No survey while their video and face snapshots are captured.

The system:
- Manages surveys and questions
- Records submissions with metadata (IP, device, browser, etc.)
- Stores answers with face detection scores
- Uploads media files (images/videos)
- Exports a full submission as a ZIP containing metadata and media

---

##  Tech Stack

- Python 3.x
- FastAPI
- MySQL
- mysql-connector-python
- Uvicorn

(No ORM, raw SQL is used for better control and transparency)

---

##  Project Structure

