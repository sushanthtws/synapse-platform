from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import frontmatter

app = FastAPI()

# CORS (tighten later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "API running"}

@app.post("/process-skill")
async def process_skill(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8")

    post = frontmatter.loads(text)

    tags = post.get("allowed-tools", [])
    if not isinstance(tags, list):
        tags = [str(tags)]

    return {
        "title": post.get("name", "Untitled Skill"),
        "description": post.get("description", "No description provided"),
        "tags": tags,
        "model": post.get("model", "N/A"),
        "effort": post.get("effort", "N/A"),
        "raw_content": text
    }