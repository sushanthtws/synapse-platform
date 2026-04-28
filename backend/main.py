from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import frontmatter
import os

from backend.refiner import refine_skill
from backend.database import init_db, insert_skill, get_all_skills, DB_NAME
from backend.repo_writer import save_skill_to_repo

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- INIT DB ----------------
@app.on_event("startup")
def startup():
    init_db()

# ---------------- HEALTH CHECK ----------------
@app.get("/")
def home():
    return {"status": "API running"}

# ---------------- GET ALL SKILLS ----------------
@app.get("/skills")
def skills():
    return get_all_skills()

# ---------------- PROCESS SKILL ----------------
@app.post("/process-skill")
async def process_skill(file: UploadFile = File(...)):

    try:
        # 1. Read markdown
        content = await file.read()
        text = content.decode("utf-8")

        # 2. Parse frontmatter (light metadata only)
        post = frontmatter.loads(text)

        tags = post.get("allowed-tools", [])
        if not isinstance(tags, list):
            tags = [str(tags)]

        # 3. Raw skill object (pre-AI)
        raw_skill = {
            "title": post.get("name", "Untitled Skill"),
            "description": post.get("description", "No description provided"),
            "tags": tags,
            "model": post.get("model", "N/A"),
            "effort": post.get("effort", "N/A"),
            "raw_content": text
        }

        # 4. AI refinement (core intelligence)
        clean_skill = refine_skill(raw_skill)

        # 5. Attach raw_content (so repo + DB has it if needed)
        clean_skill["raw_content"] = text

        # 6. Save to repo (creates folder + files)
        repo_path = save_skill_to_repo(clean_skill)

        # 7. Attach repo path
        clean_skill["repo_path"] = repo_path

        # 8. Store in DB
        insert_skill(clean_skill)

        # 9. Return UI-ready object
        return clean_skill

    except Exception as e:
        return {
            "error": "processing_failed",
            "message": str(e)
        }

# ---------------- RESET DATABASE ----------------
@app.delete("/reset-db")
def reset_db():
    try:
        db_path = DB_NAME

        if os.path.exists(db_path):
            os.remove(db_path)

        return {"status": "db cleared"}

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }