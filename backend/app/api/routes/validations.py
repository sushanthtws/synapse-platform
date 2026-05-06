from fastapi import APIRouter

router = APIRouter(tags=["validations"])


@router.get("/validations")
def list_validations():
    return []


@router.post("/validations")
def create_validation():
    return {"message": "not yet implemented"}
