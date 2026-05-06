from fastapi import APIRouter

router = APIRouter(tags=["auth"])


@router.post("/auth/login")
def login():
    return {"message": "auth not yet implemented"}
