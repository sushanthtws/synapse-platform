from openai import OpenAI
import os
import json
import re

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def safe_json_parse(text: str):
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise

def refine_skill(raw_skill: dict):

    prompt = f"""
You are a SENIOR AI SKILL CLASSIFIER.

You convert raw technical markdown into a structured skill intelligence object.

---

### TASK
Analyze WHY this skill exists and classify it.

---

### OUTPUT RULES
Return STRICT JSON only.

No markdown.
No explanation.
No extra text.

---

### OUTPUT SCHEMA

{{
  "title": "...",
  "summary": "...",
  "difficulty": "easy|medium|hard",

  "key_points": ["..."],

  "skill_type": "project_management | agile | coding | migration | productivity | optimization | devops | data | research",

  "domain": "engineering | product | operations | data | ai | infra | business",

  "intent_tags": [
    "why this skill is used (high level intent)"
  ],

  "tool_tags": [
    "Jira", "Git", "MCP", "Docker", "Notion"
  ],

  "tech_tags": [
    "Python", "React", "FastAPI"
  ]
}}

---

### RULES
- "intent_tags" = WHY (purpose / motivation)
- "tool_tags" = SOFTWARE / TOOLS USED
- "tech_tags" = PROGRAMMING / FRAMEWORKS
- Do NOT hallucinate tools if not present
- Keep tags max 5 each

---

RAW INPUT:
{json.dumps(raw_skill, indent=2)}
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a strict skill classification engine."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    content = res.choices[0].message.content
    data = safe_json_parse(content)

    return {
        "title": str(data.get("title", ""))[:60],
        "summary": str(data.get("summary", ""))[:160],
        "difficulty": data.get("difficulty", "medium"),
        "key_points": (data.get("key_points", []))[:4],

        # NEW intelligence layer
        "skill_type": data.get("skill_type", "unknown"),
        "domain": data.get("domain", "unknown"),
        "intent_tags": data.get("intent_tags", [])[:5],
        "tool_tags": data.get("tool_tags", [])[:5],
        "tech_tags": data.get("tech_tags", [])[:5],

        "llm_used": True
    }