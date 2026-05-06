from fastapi import APIRouter

router = APIRouter(tags=["compare"])


@router.get("/compare")
def compare():
    return {"message": "compare not yet implemented"}
