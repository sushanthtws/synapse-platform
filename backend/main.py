from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import frontmatter
from backend.agent import extract_skill
from backend.database import init_db, insert_skill, get_all_skills

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# init DB on startup
init_db()

@app.get("/")
def home():
    return {"status": "API running"}

# ✅ NEW: fetch all stored skills
@app.get("/skills")
def skills():
    return get_all_skills()

@app.post("/process-skill")
async def process_skill(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8")

    post = frontmatter.loads(text)

    # 🧠 AGENT STEP (IMPORTANT)
    skill = extract_skill(text, post)

    # attach raw only for download, NOT UI
    skill["raw_content"] = text

    insert_skill(skill)

    return skill

@app.delete("/reset-db")
def reset_db():
    import os
    if os.path.exists("skills.db"):
        os.remove("skills.db")
    return {"status": "db cleared"}