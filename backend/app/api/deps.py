from fastapi import Header, HTTPException
from app.core.config import settings


async def verify_api_key(x_api_key: str = Header(default="")):
    if settings.api_secret and x_api_key != settings.api_secret:
        raise HTTPException(status_code=403, detail="Invalid API key")
