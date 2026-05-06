from fastapi import APIRouter, Request

router = APIRouter(tags=["webhooks"])


@router.post("/webhooks/github")
async def github_webhook(request: Request):
    payload = await request.json()
    return {"received": True}
