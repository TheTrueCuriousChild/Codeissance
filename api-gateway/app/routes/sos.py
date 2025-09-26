from fastapi import APIRouter

router = APIRouter()

@router.get("/sos")
def get_sos():
    return {"message": "SOS requests"}