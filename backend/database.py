import sqlite3
import json

DB_NAME = "skills.db"

# ---------------- INIT DB ----------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            summary TEXT,
            difficulty TEXT,
            tags TEXT,
            key_points TEXT,

            -- NEW: AI intelligence blob
            intelligence TEXT
        )
    """)

    conn.commit()
    conn.close()


# ---------------- INSERT SKILL ----------------
def insert_skill(skill):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Extract structured fields
    title = skill.get("title")
    summary = skill.get("summary")
    difficulty = skill.get("difficulty", "medium")
    tags = skill.get("tags", [])
    key_points = skill.get("key_points", [])

    # NEW intelligence layer (everything AI-related goes here)
    intelligence = {
        "skill_type": skill.get("skill_type"),
        "domain": skill.get("domain"),
        "intent_tags": skill.get("intent_tags", []),
        "tool_tags": skill.get("tool_tags", []),
        "tech_tags": skill.get("tech_tags", [])
    }

    c.execute("""
        INSERT INTO skills (
            title,
            summary,
            difficulty,
            tags,
            key_points,
            intelligence
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        title,
        summary,
        difficulty,
        json.dumps(tags),
        json.dumps(key_points),
        json.dumps(intelligence)
    ))

    conn.commit()
    conn.close()


# ---------------- FETCH ALL SKILLS ----------------
def get_all_skills():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT * FROM skills ORDER BY id DESC")
    rows = c.fetchall()

    conn.close()

    result = []

    for r in rows:
        intelligence = json.loads(r[6]) if r[6] else {}

        result.append({
            "id": r[0],
            "title": r[1],
            "summary": r[2],
            "difficulty": r[3],
            "tags": json.loads(r[4]) if r[4] else [],
            "key_points": json.loads(r[5]) if r[5] else [],

            # NEW flattened fields for frontend filtering
            "skill_type": intelligence.get("skill_type"),
            "domain": intelligence.get("domain"),
            "intent_tags": intelligence.get("intent_tags", []),
            "tool_tags": intelligence.get("tool_tags", []),
            "tech_tags": intelligence.get("tech_tags", []),
        })

    return result