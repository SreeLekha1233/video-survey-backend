from fastapi import FastAPI
from app.routers import surveys

app = FastAPI(title="Video Survey Backend")

app.include_router(surveys.router, prefix="/api")

@app.get("/")
def health():
    return {"status": "Backend running"}
