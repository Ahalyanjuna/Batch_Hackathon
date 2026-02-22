import httpx
from app.celery_app import celery_app
from app.services.webhook import send_alert, send_master_incident
from app.services.deduplicator import check_ticket_storm

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

    # Inject ML outputs into ticket
    ticket["category"] = result.get("category")
    ticket["priority"] = result.get("priority")
    ticket["urgency_score"] = result.get("urgency_score")

    # combine text for semantic similarity
    text = ticket["subject"] + " " + ticket["description"]

    #  Deduplication logic
    is_storm, count = check_ticket_storm(text)

    if is_storm:
        print("FLASH FLOOD DETECTED → creating MASTER INCIDENT")
        send_master_incident(ticket["category"], count)
        return {
            "status": "master_incident_created",
            "cluster_size": count
        }

    # trigger webhook only when condition satisfied
    elif ticket["urgency_score"] > 0.5:
        print("ALERT CONDITION MET, SENDING WEBHOOK")
        send_alert(ticket, ticket["urgency_score"])

    # return stays same (no change to your existing API flow)
    return {
        "id": ticket["id"],
        "category": ticket["category"],
        "priority": ticket["priority"],
        "urgency_score": ticket["urgency_score"]
    }