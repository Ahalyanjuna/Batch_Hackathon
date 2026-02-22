'''
scores each available agent using skill_match×0.7 + capacity_ratio×0.3 and 
assigns the best one.
'''
from agent_registry import get_available_agents, assign_ticket

# ============================================================
# CONSTRAINT OPTIMIZATION ROUTER
# ============================================================

def route_ticket(category: str, urgency_score: float) -> dict:
    """
    Routes ticket to best available agent using constraint optimization.

    Scoring formula per agent:
        score = skill_match * 0.7 + capacity_ratio * 0.3

    Where:
        skill_match    = agent's skill score for the ticket category
        capacity_ratio = (capacity - current_load) / capacity
                         (higher = more available)

    Constraints:
        - Agent must have available capacity (current_load < capacity)
        - If no agents available → ticket goes to queue
    """

    available = get_available_agents()

    if not available:
        return {
            "assigned_agent": None,
            "status":         "QUEUED",
            "reason":         "All agents at full capacity"
        }

    scores = {}
    for agent_name, info in available.items():
        skill_match    = info["skill_vector"].get(category, 0.0)
        capacity_ratio = (info["capacity"] - info["current_load"]) / info["capacity"]

        # Weighted score
        score = 0.7 * skill_match + 0.3 * capacity_ratio
        scores[agent_name] = round(score, 4)

    # Pick agent with highest score
    best_agent = max(scores, key=scores.get)

    # Update registry
    assign_ticket(best_agent)

    return {
        "assigned_agent":  best_agent,
        "status":          "ASSIGNED",
        "category":        category,
        "urgency_score":   urgency_score,
        "routing_scores":  scores,
        "skill_match":     available[best_agent]["skill_vector"].get(category, 0.0),
    }