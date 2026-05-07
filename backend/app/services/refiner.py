import json

from openai import OpenAI

from app.core.config import settings

# ── Active provider: Groq (llama-3.1-8b-instant) ──────────────────────────────
# To switch back to OpenAI (gpt-4o-mini), comment the Groq block in `_get_client()`
# and `MODEL` below, and uncomment the OpenAI block.

_client = None


def _get_client():
    global _client
    if _client is None:
        # ── Groq (active) ─────────────────────────────────────────────────────
        _client = OpenAI(
            api_key=settings.groq_api_key or "dummy",
            base_url="https://api.groq.com/openai/v1",
        )

        # ── OpenAI (commented — uncomment to revert) ──────────────────────────
        # _client = OpenAI(
        #     api_key=settings.openai_api_key or "dummy",
        # )
    return _client


# Active model
MODEL = "llama-3.1-8b-instant"
# MODEL = "gpt-4o-mini"  # OpenAI fallback


SCHEMA = """
You are a senior system architect classifying engineering skills/playbooks.
Convert the raw skill metadata into a structured "Skill Intelligence Object".

OUTPUT FORMAT (STRICT JSON ONLY — no markdown, no commentary):
{
  "title": "Short human-readable title (Title Case)",
  "summary": "ONE concrete sentence (15–30 words) describing what this skill DOES and WHEN to use it. Avoid vague phrases like 'helps with' or 'is used for'.",
  "where_to_use": "1-2 sentences naming the concrete situations / workflows where this skill applies (e.g. 'During sprint planning when a PM needs to break a feature into JIRA epics and stories.').",
  "why_to_use": "1-2 sentences on the value: what pain does it remove or what outcome does it produce (e.g. 'Saves 30+ minutes of manual ticket drafting and ensures consistent acceptance criteria.').",
  "how_to_use": "2-4 short bullet-style steps describing how an agent would consume this skill end-to-end. Return as a single string with steps separated by ' | '.",
  "domain": "Single primary domain, e.g. 'qa-automation', 'devops', 'frontend', 'data-engineering', 'security'",
  "usage": "Single short phrase describing the trigger context, e.g. 'pre-merge review', 'sprint planning', 'incident triage'",
  "tags": ["3-6 distinct lowercase keyword tags, each 1-2 words", "no duplicates", "no commas inside a tag"],
  "tools": ["Specific tool/CLI names referenced or implied, e.g. 'playwright', 'github-actions', 'jest'"],
  "languages": ["Programming languages, e.g. 'python', 'typescript'"],
  "tech_stack": ["Frameworks/platforms, e.g. 'fastapi', 'react', 'gcp-cloud-run'"],
  "key_points": ["3-4 concrete bullet takeaways — what the skill produces or checks"],
  "repo_path": "skills/<kebab-case-title>/"
}

HARD RULES:
- tags MUST be a JSON array of separate strings — never a single comma-joined string.
- summary MUST be specific to the input content, not generic boilerplate.
- If a field is unknown, return an empty array [] (never null, never a string).
- MAX 6 tags, MAX 4 key_points.
"""


def refine_skill(raw_skill: dict):
    # Only send metadata to the AI — never the full raw_content (too large)
    ai_input = {k: v for k, v in raw_skill.items() if k not in ("raw_content", "file_listing")}
    if "description" in ai_input:
        ai_input["description"] = ai_input["description"][:500]

    # Include a trimmed slice of raw content so the model has substance to summarize
    raw_excerpt = (raw_skill.get("raw_content") or "")[:2000]

    # File listing gives the model strong signal for tags/tools
    file_listing = raw_skill.get("file_listing") or []
    listing_text = "\n".join(f"- {p}" for p in file_listing[:50]) if file_listing else "(none)"

    prompt = (
        f"Skill metadata:\n{json.dumps(ai_input, indent=2)}\n\n"
        f"Bundle file listing (use these filenames as strong signals for tags/tools — "
        f"e.g. 'jira_template.md' implies the tag 'jira'):\n{listing_text}\n\n"
        f"Skill body excerpt (first 2000 chars):\n{raw_excerpt}\n\n"
        f"{SCHEMA}"
    )

    res = _get_client().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a strict JSON system classifier. Return only valid JSON matching the requested schema."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    content = res.choices[0].message.content
    try:
        data = json.loads(content)
    except Exception:
        return {
            "title": raw_skill.get("title", "parse_error"),
            "summary": raw_skill.get("description", "")[:120],
            "domain": "unknown", "usage": "unknown",
            "where_to_use": "", "why_to_use": "", "how_to_use": "",
            "tags": [], "tools": [], "languages": [], "tech_stack": [],
            "key_points": [], "repo_path": "skills/unknown/"
        }

    # Defensive normalization: if model returns a comma-joined string, split it.
    for key in ("tags", "tools", "languages", "tech_stack", "key_points"):
        val = data.get(key)
        if isinstance(val, str):
            data[key] = [s.strip() for s in val.split(",") if s.strip()]
        elif not isinstance(val, list):
            data[key] = []

    data["repo_path"] = data.get("repo_path") or f"skills/{data.get('title','unknown').lower().replace(' ','-')}/"
    return data
