from fastapi import APIRouter

router = APIRouter(tags=["Surveys"])

@router.get("/ping")
def ping():
    return {"message": "Surveys router working"}
