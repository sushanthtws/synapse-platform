import sqlite3
import json
from collections import Counter
from datetime import datetime

DB_NAME = "skills.db"


# ---------------- LOAD DATA ----------------
def load_skills():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT title, tags, difficulty FROM skills")
    rows = c.fetchall()

    conn.close()

    skills = []
    for r in rows:
        skills.append({
            "title": r[0],
            "tags": json.loads(r[1]) if r[1] else [],
            "difficulty": r[2]
        })

    return skills


# ---------------- SIMPLE INSIGHT ENGINE ----------------
def generate_insights():
    skills = load_skills()

    tag_counter = Counter()
    domain_counter = Counter()
    difficulty_counter = Counter()

    # lightweight domain mapping
    DOMAIN_MAP = {
        "react": "frontend",
        "next.js": "frontend",
        "vue": "frontend",
        "angular": "frontend",

        "fastapi": "backend",
        "django": "backend",
        "express": "backend",

        "openai": "ai",
        "langchain": "ai",
        "rag": "ai",
        "claude": "ai",

        "docker": "devops",
        "kubernetes": "devops",
        "terraform": "devops",

        "python": "language",
        "go": "language",
        "typescript": "language",
        "java": "language"
    }

    for s in skills:
        tags = [t.lower() for t in s.get("tags", [])]

        for t in tags:
            tag_counter[t] += 1

            domain = DOMAIN_MAP.get(t)
            if domain:
                domain_counter[domain] += 1

        difficulty_counter[s.get("difficulty", "unknown")] += 1

    total = len(skills) or 1

    # top signals
    top_tags = tag_counter.most_common(5)
    top_domains = domain_counter.most_common(3)

    dominant_domain = top_domains[0][0] if top_domains else "mixed"
    dominant_tag = top_tags[0][0] if top_tags else "unknown"

    # simple trend heuristic
    trend = "balanced"
    if domain_counter.get("ai", 0) > domain_counter.get("backend", 0):
        trend = "AI-heavy activity"
    elif domain_counter.get("frontend", 0) > domain_counter.get("backend", 0):
        trend = "frontend-driven activity"
    elif domain_counter.get("backend", 0) > domain_counter.get("frontend", 0):
        trend = "backend-heavy activity"

    # ---------------- FINAL INSIGHT OBJECT ----------------
    return {
        "timestamp": datetime.utcnow().isoformat(),

        "total_skills": total,

        "top_tags": [
            {"tag": t[0], "count": t[1]} for t in top_tags
        ],

        "top_domains": [
            {"domain": d[0], "count": d[1]} for d in top_domains
        ],

        "difficulty_distribution": dict(difficulty_counter),

        "summary": build_summary(
            total,
            dominant_tag,
            dominant_domain,
            trend
        )
    }


# ---------------- HUMAN READABLE SUMMARY ----------------
def build_summary(total, tag, domain, trend):
    return (
        f"The repository currently contains {total} skills. "
        f"The most frequent skill is '{tag}', with '{domain}' being the dominant domain. "
        f"Overall activity shows {trend}, indicating the system is evolving in that direction."
    )


# ---------------- PUBLIC API ----------------
def get_repo_insights():
    return generate_insights()