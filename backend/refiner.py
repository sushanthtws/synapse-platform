from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def refine_skill(raw_skill: dict):
    prompt = f"""
You are a skill summarizer.

Convert this raw extracted skill into a CLEAN UI OBJECT.

RULES:
- Remove all technical noise
- Do NOT include markdown or instructions
- Keep it simple and user-facing
- Max 1 sentence summary
- Max 4 key points
- Max 5 tags

OUTPUT JSON ONLY:

{{
  "title": "...",
  "summary": "...",
  "tags": ["..."],
  "difficulty": "easy|medium|hard",
  "key_points": ["..."]
}}

RAW INPUT:
{json.dumps(raw_skill, indent=2)}
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a strict JSON transformer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return json.loads(res.choices[0].message.content)