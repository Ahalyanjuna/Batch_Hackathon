import httpx
from app.celery_app import celery_app

ML_SERVICE_URL = "http://localhost:8001/classify"


@celery_app.task
def process_ticket_task(ticket: dict):

    response = httpx.post(
        ML_SERVICE_URL,
        json={
            "subject": ticket["subject"],
            "description": ticket["description"]
        }
    )

    result = response.json()

    return {
        "id": ticket["id"],
        "category": result["category"],
        "priority": result["priority"],
        "urgency_score": result["urgency_score"]
    }