import re

def clean_text(text):
    # remove code blocks completely
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

    # remove markdown symbols
    text = re.sub(r"[#*_>`-]", "", text)

    # collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def extract_skill(text, post):

    safe_text = clean_text(text)

    sentences = [s.strip() for s in safe_text.split(".") if len(s.strip()) > 20]

    return {
        "title": post.get("name", "Untitled Skill"),
        "description": safe_text[:140],   # 👈 HARD LIMIT
        "tags": (post.get("allowed-tools", []) or [])[:5],
        "key_points": sentences[:4],      # 👈 ALWAYS ARRAY
        "difficulty": "medium"
    }