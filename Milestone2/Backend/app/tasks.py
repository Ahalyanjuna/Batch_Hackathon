import httpx
from app.celery_app import celery_app

ML_SERVICE_URL = "http://localhost:8001/classify"


@celery_app.task(bind=True)
def process_ticket_task(self, ticket_data: dict):

    subject = ticket_data["subject"]
    description = ticket_data["description"]
    urgency_score = ticket_data["urgency_score"]

    try:
        response = httpx.post(
            ML_SERVICE_URL,
            json={
                "subject": subject,
                "description": description
            },
            timeout=10.0
        )

        result = response.json()

        return {
            "ticket_id": ticket_data["id"],
            "category": result.get("category"),
            "priority": result.get("priority"),
            "urgency_score": urgency_score,
            "status": "COMPLETED"
        }

    except Exception as e:
        return {
            "ticket_id": ticket_data["id"],
            "error": str(e),
            "status": "FAILED"
        }