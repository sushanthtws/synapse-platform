import json
from openai import OpenAI

import os

def get_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SCHEMA = """
You MUST return ONLY valid JSON.

No explanation.
No markdown.
No extra text.

Return exactly this format:

{
  "title": string (max 60 chars),
  "description": string (max 140 chars),
  "tags": array of max 5 strings,
  "key_points": array of max 4 strings,
  "difficulty": "easy" | "medium" | "hard"
}
"""

def get_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_skill(text, post):

    client = get_client()

    prompt = f"""
Convert this markdown skill into structured JSON.

RULES:
- Remove all code blocks
- Extract only learning information
- Keep it concise
- STRICT JSON ONLY

Title hint: {post.get('name', '')}
Allowed tools: {post.get('allowed-tools', [])}

CONTENT:
{text}

{SCHEMA}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a strict JSON generator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    raw = response.choices[0].message.content

    try:
        data = json.loads(raw)   # 👈 strict enforcement
    except Exception:
        # fallback safety
        return {
            "title": "Parse Error",
            "description": text[:140],
            "tags": [],
            "key_points": [],
            "difficulty": "medium",
            "llm_error": True
        }

    # final UI safety trim
    return {
        "title": str(data.get("title", ""))[:60],
        "description": str(data.get("description", ""))[:140],
        "tags": (data.get("tags", []))[:5],
        "key_points": (data.get("key_points", []))[:4],
        "difficulty": data.get("difficulty", "medium"),
        "llm_used": True   # 👈 IMPORTANT DEBUG FLAG
    }