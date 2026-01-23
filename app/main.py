from fastapi import FastAPI
from app.routers import surveys, submissions, export

app = FastAPI(title="Video Survey Backend")

app.include_router(surveys.router, prefix="/api")
app.include_router(submissions.router, prefix="/api")
app.include_router(export.router, prefix="/api")

@app.get("/")
def health():
    return {"status": "Backend running"}

