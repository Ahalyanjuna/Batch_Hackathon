

from app.services.circuit_breaker import classify_with_circuit_breaker
from app.services.router import route_to_best_agent

async def process_ticket_pipeline(ticket_dict):

    subject = ticket_dict["subject"]
    description = ticket_dict["description"]

    # 1️⃣ Classification with failover
    result = await classify_with_circuit_breaker(subject, description)

    category = result["category"]
    urgency_score = result["urgency_score"]

    # 2️⃣ Skill routing
    assigned_agent = route_to_best_agent(category)

    return {
        "ticket_id": ticket_dict.get("id"),
        "category": category,
        "urgency_score": urgency_score,
        "assigned_agent": assigned_agent,
        "model_used": result.get("model_used", "ML2")
    }