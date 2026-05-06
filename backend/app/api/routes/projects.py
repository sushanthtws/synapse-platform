from fastapi import APIRouter

router = APIRouter(tags=["projects"])


@router.get("/projects")
def list_projects():
    return []


@router.post("/projects")
def create_project():
    return {"message": "not yet implemented"}
