import requests
from app.config import MODE, SLACK_WEBHOOK_URL, DISCORD_WEBHOOK_URL, MOCK_WEBHOOK_URL

def _send_to_slack(ticket, score):
    payload = {
        "text": (
            f"High Urgency Ticket!\n"
            f"ID: {ticket['id']}\n"
            f"Category: {ticket['category']}\n"
            f"Score: {score:.2f}\n"
            f"Message: {ticket['text']}"
        )
    }
    requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=3)

def _send_to_discord(ticket, score):
    payload = {
        "content": (
            f"🚨 **High Urgency Ticket!**\n\n"
            f"**Category:** {ticket['category']}\n"
            f"**Urgency Score:** {score:.2f}\n"
            f"**Message:** {ticket.get('description', ticket.get('text', 'N/A'))}"
        )
    }
    requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=3)

def _send_to_mock(ticket, score):
    payload = {
        "id": ticket["id"],
        "category": ticket["category"],
        "score": float(score),
        "message": ticket["text"]
    }
    requests.post(MOCK_WEBHOOK_URL, json=payload, timeout=3)

def send_master_incident(category, count):
    payload = {
        "content": (
            f"🚨🚨 **MASTER INCIDENT DETECTED** 🚨🚨\n\n"
            f"**Category:** {category}\n"
            f"**Affected Tickets:** {count}\n"
            f"**Status:** Flash Flood Suppressed\n"
        )
    }

    if MODE == "REAL":
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=3)
    else:
        requests.post(MOCK_WEBHOOK_URL, json=payload, timeout=3)

def send_alert(ticket, score):
    """
    Single function your worker will call.
    """
    if MODE == "REAL":
        _send_to_discord(ticket, score)
    else:
        _send_to_mock(ticket, score)