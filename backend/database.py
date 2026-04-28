import sqlite3
import json

DB_NAME = "skills.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            tags TEXT,
            model TEXT,
            effort TEXT,
            raw_content TEXT
        )
    """)

    conn.commit()
    conn.close()


def insert_skill(skill):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        INSERT INTO skills (title, description, tags, model, effort, raw_content)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        skill["title"],
        skill["description"],
        json.dumps(skill["tags"]),
        skill["model"],
        skill["effort"],
        skill["raw_content"]
    ))

    conn.commit()
    conn.close()


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
            "description": r[2],
            "tags": json.loads(r[3]),
            "model": r[4],
            "effort": r[5],
            "raw_content": r[6],
        })

    return result