

AGENT_REGISTRY = {
    "Agent_A": {
        "skill_vector": {
            "Technical": 0.9,
            "Billing": 0.2,
            "Legal": 0.1
        },
        "capacity": 5,
        "current_load": 0
    },
    "Agent_B": {
        "skill_vector": {
            "Technical": 0.3,
            "Billing": 0.8,
            "Legal": 0.2
        },
        "capacity": 5,
        "current_load": 0
    }
}


def get_available_agents():
    return {
        name: info
        for name, info in AGENT_REGISTRY.items()
        if info["current_load"] < info["capacity"]
    }


def assign_ticket(agent_name):
    AGENT_REGISTRY[agent_name]["current_load"] += 1


def release_ticket(agent_name):
    AGENT_REGISTRY[agent_name]["current_load"] -= 1