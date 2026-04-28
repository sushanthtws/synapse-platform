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
            tags TEXT,
            difficulty TEXT,
            key_points TEXT
        )
    """)

    conn.commit()
    conn.close()


# ---------------- INSERT SKILL ----------------
def insert_skill(skill):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        INSERT INTO skills (title, summary, tags, difficulty, key_points)
        VALUES (?, ?, ?, ?, ?)
    """, (
        skill["title"],
        skill["summary"],
        json.dumps(skill.get("tags", [])),
        skill.get("difficulty", "medium"),
        json.dumps(skill.get("key_points", []))
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
            "tags": json.loads(r[3]),
            "difficulty": r[4],
            "key_points": json.loads(r[5])
        })

    return result