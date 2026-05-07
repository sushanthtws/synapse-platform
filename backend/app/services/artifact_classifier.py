"""Rule-based classification of agent-facing artifacts in a skill bundle.

Maps each uploaded file (by relative path + filename) to one of a known set
of artifact types so the UI can show users *what* is in a skill bundle and
the agent can understand how each file is meant to be consumed.
"""
import os
from typing import List, Tuple


# Ordered: first match wins. Each rule is (predicate, type, role).
# Predicates take (lowered_full_path, lowered_basename, ext).
_RULES: List[Tuple] = [
    # Primary skill documents
    (lambda p, b, e: b in ("skill.md", "skills.md"), "skill_doc", "Primary skill definition (SKILL.md)"),
    (lambda p, b, e: b == "readme.md", "readme", "Skill README / overview"),
    (lambda p, b, e: b == "claude.md", "claude_md", "Claude Code project instructions"),
    (lambda p, b, e: b == "agents.md", "agents_md", "Multi-agent orchestration rules"),
    (lambda p, b, e: b == ".cursorrules", "cursor_rules", "Cursor IDE rules"),
    (lambda p, b, e: b == ".windsurfrules", "windsurf_rules", "Windsurf IDE rules"),

    # Folder-based classifiers
    (lambda p, b, e: "/slash_commands/" in p or "/commands/" in p or "/.claude/commands/" in p,
     "slash_command", "Slash command definition"),
    (lambda p, b, e: "/subagents/" in p or "/agents/" in p,
     "subagent", "Subagent definition"),
    (lambda p, b, e: "/hooks/" in p or b.endswith(".hook.sh") or b.endswith(".hook.py"),
     "hook", "Pre/post tool-call hook"),
    (lambda p, b, e: "/evals/" in p or "/tests/" in p,
     "eval", "Evaluation / test suite"),
    (lambda p, b, e: "/prompts/" in p or b.endswith(".prompt.md") or b.endswith(".prompt.txt"),
     "prompt", "Reusable prompt"),
    (lambda p, b, e: "/templates/" in p,
     "template", "Template file"),

    # MCP configs
    (lambda p, b, e: "mcp" in b and e == ".json", "mcp_config", "MCP server configuration"),
    (lambda p, b, e: "/.mcp/" in p, "mcp_config", "MCP server configuration"),

    # Other docs
    (lambda p, b, e: e == ".md", "doc", "Markdown document"),
    (lambda p, b, e: e in (".json", ".yaml", ".yml", ".toml"), "config", "Configuration file"),
    (lambda p, b, e: e in (".py", ".js", ".ts", ".sh"), "script", "Script / source file"),
]


def classify(rel_path: str) -> Tuple[str, str]:
    """Return (type, role) for a file's relative path within the skill folder."""
    p = "/" + rel_path.lower().lstrip("/")
    b = os.path.basename(p)
    _, e = os.path.splitext(b)
    for predicate, type_, role in _RULES:
        try:
            if predicate(p, b, e):
                return type_, role
        except Exception:
            continue
    return "other", "Unclassified"


# Priority order for picking the *primary* skill markdown when a folder is uploaded
_PRIMARY_PRIORITY = ["skill.md", "skills.md", "readme.md"]


def pick_primary_markdown(rel_paths: List[str]) -> str | None:
    """Pick the most appropriate primary markdown file from a list of relative paths."""
    lowered = {p.lower(): p for p in rel_paths}
    # 1. Known canonical filenames at any depth, prioritising shallowest
    for name in _PRIMARY_PRIORITY:
        candidates = [orig for low, orig in lowered.items() if os.path.basename(low) == name]
        if candidates:
            candidates.sort(key=lambda x: x.count("/"))
            return candidates[0]
    # 2. Any .md file, shallowest first
    md = [orig for low, orig in lowered.items() if low.endswith(".md")]
    if md:
        md.sort(key=lambda x: x.count("/"))
        return md[0]
    return None
