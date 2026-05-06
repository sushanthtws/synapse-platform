import json

from openai import OpenAI

from app.core.config import settings

# Using Groq — free tier, OpenAI-compatible API (Llama 3)
# Client is initialized lazily so missing key doesn't crash on import
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.groq_api_key or "dummy",
            base_url="https://api.groq.com/openai/v1",
        )
    return _client

SCHEMA = """
You are a senior system architect and skill classifier.
Convert raw extracted skill into a structured "Skill Intelligence Object".

OUTPUT FORMAT (STRICT JSON ONLY):
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
RULES: NO markdown, NO explanation, MAX 1 sentence summary, MAX 5 tags, MAX 4 key_points
"""


def refine_skill(raw_skill: dict):
    # Only send metadata to the AI — never the full raw_content (too large)
    ai_input = {k: v for k, v in raw_skill.items() if k != "raw_content"}
    # Truncate description to 500 chars to stay within token limits
    if "description" in ai_input:
        ai_input["description"] = ai_input["description"][:500]

    prompt = f"Analyze this skill:\n{json.dumps(ai_input, indent=2)}\n\n{SCHEMA}"
    res = _get_client().chat.completions.create(
        model="llama-3.1-8b-instant",
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
            "domain": "unknown", "usage": "unknown", "difficulty": "medium",
            "tags": [], "tools": [], "languages": [], "tech_stack": [],
            "key_points": [], "repo_path": "skills/unknown/"
        }
    data["repo_path"] = data.get("repo_path") or f"skills/{data.get('title','unknown').lower().replace(' ','-')}/"
    return data
