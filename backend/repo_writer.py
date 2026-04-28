import os
import json
import re


BASE_SKILL_DIR = os.getenv("BASE_SKILL_DIR", "/tmp/skills")


# ---------------- UTIL ----------------
def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip("-")


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


# ---------------- REQUIREMENTS GENERATOR ----------------
def generate_requirements(skill):

    deps = set()

    tool_map = {
        "openai": "openai",
        "langchain": "langchain",
        "fastapi": "fastapi",
        "django": "django",
        "flask": "flask",
        "react": "# frontend",
        "next.js": "# frontend",
        "postgresql": "psycopg2-binary",
        "redis": "redis",
    }

    for tool in skill.get("tools", []) + skill.get("tech_stack", []):
        t = tool.lower()
        if t in tool_map:
            deps.add(tool_map[t])

    # remove comments like "# frontend"
    deps = [d for d in deps if not d.startswith("#")]

    return "\n".join(sorted(deps)) if deps else "# no dependencies detected"


# ---------------- README GENERATOR ----------------
def generate_readme(skill):

    return f"""
# {skill.get("title")}

## 📌 Summary
{skill.get("summary")}

## 🧠 Domain
{skill.get("domain")}

## 🎯 Usage
{skill.get("usage")}

## 🏷 Tags
{", ".join(skill.get("tags", []))}

## ⚙️ Tech Stack
{", ".join(skill.get("tech_stack", []))}

## 🧰 Tools
{", ".join(skill.get("tools", []))}

## 💻 Languages
{", ".join(skill.get("languages", []))}

## 🔑 Key Points
{"".join([f"- {kp}\n" for kp in skill.get("key_points", [])])}
"""


# ---------------- MAIN WRITER ----------------
def save_skill_to_repo(skill: dict):

    # 1. create folder name
    slug = slugify(skill.get("title", "unknown"))
    repo_path = os.path.join(BASE_SKILL_DIR, slug)

    ensure_dir(repo_path)

    # 2. skill_card.json (main structured asset)
    skill_card_path = os.path.join(repo_path, "skill_card.json")

    with open(skill_card_path, "w") as f:
        json.dump(skill, f, indent=2)

    # 3. README.md
    readme_path = os.path.join(repo_path, "README.md")

    with open(readme_path, "w") as f:
        f.write(generate_readme(skill))

    # 4. requirements.txt
    req_path = os.path.join(repo_path, "requirements.txt")

    with open(req_path, "w") as f:
        f.write(generate_requirements(skill))

    # 5. return repo path for DB
    return repo_path