from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


SCHEMA = """
You are a senior system architect and skill classifier.

Convert raw extracted skill into a structured "Skill Intelligence Object".

You MUST classify intelligently:

────────────────────────────
1. DOMAIN (why this skill exists)
────────────────────────────
Choose ONE primary:
- project_management
- software_engineering
- system_design
- migration
- optimization
- automation
- ai_ml
- devops
- data_engineering
- productivity
- research

────────────────────────────
2. USAGE (what it is used for)
────────────────────────────
Examples:
- workflow optimization
- system migration
- API integration
- LLM orchestration
- performance tuning
- task automation
- team coordination

────────────────────────────
3. TECH EXTRACTION
────────────────────────────
Extract separately:
- tools (APIs, frameworks like OpenAI, LangChain)
- languages (Python, Go, JS, Java, etc.)
- tech_stack (React, FastAPI, Kubernetes, etc.)

────────────────────────────
4. OUTPUT FORMAT (STRICT JSON ONLY)
────────────────────────────

{
  "title": "...",
  "summary": "...",

  "domain": "...",
  "usage": "...",

  "difficulty": "easy|medium|hard",

  "tags": ["..."],

  "tools": ["..."],
  "languages": ["..."],
  "tech_stack": ["..."],

  "key_points": ["..."],

  "repo_path": "skills/<kebab-case-title>/"
}

────────────────────────────
RULES:
- NO markdown
- NO explanation
- MAX 1 sentence summary
- MAX 5 tags
- MAX 4 key_points
- Always infer intelligently, do not leave empty arrays unless truly unknown
"""


def refine_skill(raw_skill: dict):

    prompt = f"""
Analyze this skill and convert it into structured system-ready format.

RAW INPUT:
{json.dumps(raw_skill, indent=2)}

{SCHEMA}
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a strict JSON system classifier."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    content = res.choices[0].message.content

    try:
        data = json.loads(content)
    except Exception:
        return {
            "title": raw_skill.get("title", "parse_error"),
            "summary": raw_skill.get("description", "")[:120],

            "domain": "unknown",
            "usage": "unknown",

            "difficulty": "medium",

            "tags": [],
            "tools": [],
            "languages": [],
            "tech_stack": [],

            "key_points": [],

            "repo_path": "skills/unknown/"
        }

    # safety normalization
    data["repo_path"] = data.get("repo_path") or f"skills/{data.get('title','unknown').lower().replace(' ','-')}/"

    return data