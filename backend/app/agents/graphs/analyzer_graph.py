from app.agents.nodes.analysis_nodes import analyze_skill_node


def run_analyzer(raw_skill: dict) -> dict:
    return analyze_skill_node(raw_skill)
