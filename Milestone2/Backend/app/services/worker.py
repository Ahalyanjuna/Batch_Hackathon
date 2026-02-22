import requests
from app.services.webhook import send_alert

ML_SERVICE_URL = "http://127.0.0.1:8001/classify"


def call_ml_service(ticket):
    """
    Calls your Milestone2 ML model service
    """
    try:
        response = requests.post(
            ML_SERVICE_URL,
            json={
                "subject": ticket["subject"],
                "description": ticket["description"]
            },
            timeout=5
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print("ML Service error:", e)
        return None


def process_ticket(ticket: dict):
    """
    Main worker logic (microservice orchestrator)
    """
    result = call_ml_service(ticket)

    if result is None:
        print("Skipping ticket due to ML failure")
        return

    category = result.get("category")
    score = result.get("urgency_score")

    ticket["category"] = category

    print(f"Processed Ticket {ticket['id']} → category={category}, score={score:.2f}")

    #  trigger webhook service
    if score > 0.5:
        print("🔥 ALERT CONDITION MET, SENDING WEBHOOK")
        send_alert(ticket, score)


if __name__ == "__main__":
    samples = [
        {
            "id": 1,
            "subject": "Production Down",
            "description": "My system is broken and production is down ASAP"
        },
        {
            "id": 2,
            "subject": "Invoice Request",
            "description": "Need invoice copy for last month bill"
        },
        {
            "id": 3,
            "subject": "Service degraded",
            "description": "Service degraded, urgent assistance required immediately"
        },
        {
            "id": 4,
            "subject": "Critical outage",
            "description": "Production system broken urgent asap immediately down"
        }
    ]

    for t in samples:
        process_ticket(t)