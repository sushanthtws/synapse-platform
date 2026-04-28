import json
from openai import OpenAI

import os

def get_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SCHEMA = """
Return ONLY valid JSON in this format:
{
  "title": string (max 60 chars),
  "description": string (max 140 chars),
  "tags": array of max 5 strings,
  "key_points": array of max 4 strings,
  "difficulty": "easy" | "medium" | "hard"
}
"""

def extract_skill(text, post):

    prompt = f"""
You are a skill extraction system.

Convert the following markdown into structured skill data.

Rules:
- Remove code blocks
- Extract meaningful learning points
- Keep output concise
- No markdown in output
- STRICT JSON only

User metadata:
name: {post.get('name', 'Untitled')}
allowed-tools: {post.get('allowed-tools', [])}

Content:
{text}

{SCHEMA}
"""
    client = get_client()
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You output only strict JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content

        # enforce JSON safety
        data = json.loads(content)

        return data

    except Exception as e:
        # fallback safe output
        return {
            "title": post.get("name", "Untitled Skill"),
            "description": text[:140],
            "tags": [],
            "key_points": [],
            "difficulty": "medium"
        }