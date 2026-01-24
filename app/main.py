from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import surveys, submissions, export

app = FastAPI(title="Video Survey Backend")

# ✅ ADD THIS CORS CONFIG
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(surveys.router, prefix="/api")
app.include_router(submissions.router, prefix="/api")
app.include_router(export.router, prefix="/api")

@app.get("/")
def health():
    return {"status": "Backend running"}
