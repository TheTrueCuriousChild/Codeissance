from fastapi import APIRouter

router = APIRouter()

@router.get("/bloodbanks")
def get_bloodbanks():
    return {"message": "List of blood banks"}