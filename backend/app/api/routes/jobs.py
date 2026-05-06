from fastapi import APIRouter

router = APIRouter(tags=["jobs"])


@router.get("/jobs")
def list_jobs():
    return []
