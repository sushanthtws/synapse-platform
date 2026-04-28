import sqlite3
import json
import os

DB_NAME = os.getenv("DB_NAME", "/tmp/skills.db")

# ---------------- INIT DB ----------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT,
            summary TEXT,

            domain TEXT,              -- project management / migration / optimization / etc
            usage TEXT,               -- why skill is used
            difficulty TEXT,

            tags TEXT,                -- generic tags (UI chips)
            tools TEXT,               -- APIs / frameworks
            languages TEXT,           -- Python, Go, JS etc
            tech_stack TEXT,          -- React, FastAPI, etc

            key_points TEXT,

            repo_path TEXT,           -- where skill is stored in repo

            raw_content TEXT
        )
    """)

    conn.commit()
    conn.close()


# ---------------- INSERT SKILL ----------------
def insert_skill(skill):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        INSERT INTO skills (
            title, summary,
            domain, usage, difficulty,
            tags, tools, languages, tech_stack,
            key_points,
            repo_path,
            raw_content
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        skill.get("title"),
        skill.get("summary"),

        skill.get("domain"),
        skill.get("usage"),
        skill.get("difficulty", "medium"),

        json.dumps(skill.get("tags", [])),
        json.dumps(skill.get("tools", [])),
        json.dumps(skill.get("languages", [])),
        json.dumps(skill.get("tech_stack", [])),

        json.dumps(skill.get("key_points", [])),

        skill.get("repo_path"),

        skill.get("raw_content")
    ))

    conn.commit()
    conn.close()


# ---------------- FETCH ALL SKILLS ----------------
def get_all_skills():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT * FROM skills")
    rows = c.fetchall()

    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "title": r[1],
            "summary": r[2],

            "domain": r[3],
            "usage": r[4],
            "difficulty": r[5],

            "tags": json.loads(r[6] or "[]"),
            "tools": json.loads(r[7] or "[]"),
            "languages": json.loads(r[8] or "[]"),
            "tech_stack": json.loads(r[9] or "[]"),

            "key_points": json.loads(r[10] or "[]"),

            "repo_path": r[11],
            "raw_content": r[12]
        })

    return result