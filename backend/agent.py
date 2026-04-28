import re

def extract_skill(text, post):
    """
    Converts messy markdown into structured skill object
    """

    # Clean text
    clean_text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

    # Extract key points (simple heuristic)
    sentences = [s.strip() for s in clean_text.split("\n") if len(s.strip()) > 20]

    key_points = sentences[:4]  # limit UI overload

    tags = post.get("allowed-tools", [])
    if not isinstance(tags, list):
        tags = [str(tags)]

    return {
        "title": post.get("name", "Untitled Skill"),
        "description": post.get("description", clean_text[:180]),
        "tags": tags[:5],  # limit tags
        "key_points": key_points,
        "difficulty": "medium"
    }