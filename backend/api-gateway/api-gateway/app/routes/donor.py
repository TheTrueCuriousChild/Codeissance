from fastapi import APIRouter

router = APIRouter()

@router.get("/donors")
def get_donors():
    return {"message": "List of donors"}