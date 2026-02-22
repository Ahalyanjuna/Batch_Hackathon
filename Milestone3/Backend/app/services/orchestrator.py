import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml2_ml_pipeline'))

from circuit_breaker import run_with_circuit_breaker
from router import route_ticket
from agent_registry import get_registry_status
from inference import predict_ticket  # ML2 transformer inference

# ============================================================
# MAIN ORCHESTRATOR
# ============================================================

def process_ticket(text: str) -> dict:
    """
    Full pipeline:
    1. Circuit Breaker → ML2 transformer (fallback to ML1 if slow/failing)
    2. Skill-Based Router → assign to best available agent
    """
    print(f"\n{'='*60}")
    print(f"Processing: {text[:60]}...")

    # Step 1: Predict with circuit breaker protection
    prediction = run_with_circuit_breaker(text, predict_ticket)

    category      = prediction.get("predicted_category", "General inquiry")
    urgency_score = prediction.get("urgency_score", 0.5)
    model_used    = prediction.get("model_used", "Unknown")
    circuit_state = prediction.get("circuit_state", "UNKNOWN")

    print(f"  [Model]   {model_used} | Circuit: {circuit_state}")
    print(f"  [Result]  Category={category} | Urgency={urgency_score}")

    # Step 2: Route to best agent
    routing = route_ticket(category, urgency_score)
    agent   = routing.get("assigned_agent", "QUEUE")

    print(f"  [Router]  Assigned to: {agent} | Status: {routing['status']}")

    return {
        "ticket_text":    text,
        "category":       category,
        "urgency_score":  urgency_score,
        "model_used":     model_used,
        "circuit_state":  circuit_state,
        "assigned_agent": agent,
        "routing_status": routing["status"],
        "routing_scores": routing.get("routing_scores", {}),
    }


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":
    test_tickets = [
        "Server down, production impacted badly",
        "I suspect a data breach has exposed my information tied to Fitbit Versa Smartwatch.",
        "Need invoice copy for accounting records",
        "UPI payment successful but order not confirmed",
        "There has been a violation of my consumer rights. I require immediate legal clarification.",
    ]

    for ticket in test_tickets:
        result = process_ticket(ticket)
        print(f"  [Final]   {result}")

    print(f"\n{'='*60}")
    print("Agent Registry Status:")
    for agent, status in get_registry_status().items():
        print(f"  {agent}: {status}")