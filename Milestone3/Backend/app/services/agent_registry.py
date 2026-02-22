'''
maintains 4 agents (A=Tech, B=Billing, C=Legal, D=Generalist) 
with skill vectors and live capacity tracking.
'''

# ============================================================
# AGENT REGISTRY — Skill Vectors + Capacity Tracking
# ============================================================

# Each agent has:
# - skill_vector: % expertise per category (must sum to 1.0)
# - capacity: max tickets they can handle simultaneously
# - current_load: tickets currently assigned

AGENT_REGISTRY = {
    "Agent_A": {
        "skill_vector": {
            "Technical issue":  0.80,
            "Billing":          0.10,
            "General inquiry":  0.05,
            "Legal inquiry":    0.05,
        },
        "capacity":     5,
        "current_load": 0,
    },
    "Agent_B": {
        "skill_vector": {
            "Technical issue":  0.10,
            "Billing":          0.75,
            "General inquiry":  0.10,
            "Legal inquiry":    0.05,
        },
        "capacity":     5,
        "current_load": 0,
    },
    "Agent_C": {
        "skill_vector": {
            "Technical issue":  0.05,
            "Billing":          0.10,
            "General inquiry":  0.15,
            "Legal inquiry":    0.70,
        },
        "capacity":     5,
        "current_load": 0,
    },
    "Agent_D": {
        "skill_vector": {
            "Technical issue":  0.30,
            "Billing":          0.30,
            "General inquiry":  0.30,
            "Legal inquiry":    0.10,
        },
        "capacity":     8,   # generalist, higher capacity
        "current_load": 0,
    },
}


def get_available_agents() -> dict:
    """Returns agents who still have capacity."""
    return {
        name: info
        for name, info in AGENT_REGISTRY.items()
        if info["current_load"] < info["capacity"]
    }


def assign_ticket(agent_name: str):
    """Increment agent load when a ticket is assigned."""
    if agent_name in AGENT_REGISTRY:
        AGENT_REGISTRY[agent_name]["current_load"] += 1


def complete_ticket(agent_name: str):
    """Decrement agent load when a ticket is resolved."""
    if agent_name in AGENT_REGISTRY:
        load = AGENT_REGISTRY[agent_name]["current_load"]
        AGENT_REGISTRY[agent_name]["current_load"] = max(0, load - 1)


def get_registry_status() -> dict:
    """Returns current load status of all agents."""
    return {
        name: {
            "current_load": info["current_load"],
            "capacity":     info["capacity"],
            "available":    info["current_load"] < info["capacity"]
        }
        for name, info in AGENT_REGISTRY.items()
    }