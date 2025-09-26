from fastapi import APIRouter

router = APIRouter()

@router.get("/hospitals")
def get_hospitals():
    return {"message": "List of hospitals"}