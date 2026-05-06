from fastapi import APIRouter

router = APIRouter(tags=["chat"])


@router.post("/chat")
def chat():
    return {"reply": "chat not yet implemented"}
