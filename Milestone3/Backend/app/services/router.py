'''
scores each available agent using skill_match×0.7 + capacity_ratio×0.3 and 
assigns the best one.
'''
from app.services.agent_registry import (
    get_available_agents,
    assign_ticket
)


def route_to_best_agent(category: str):

    agents = get_available_agents()

    if not agents:
        return None

    best_agent = None
    best_score = -1

    for name, info in agents.items():

        skill_score = info["skill_vector"].get(category, 0)

        load_ratio = info["current_load"] / info["capacity"]

        final_score = skill_score * (1 - load_ratio)

        if final_score > best_score:
            best_score = final_score
            best_agent = name

    if best_agent:
        assign_ticket(best_agent)

    return best_agent
