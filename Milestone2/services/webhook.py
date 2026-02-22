import requests
from config import MODE, SLACK_WEBHOOK_URL, DISCORD_WEBHOOK_URL, MOCK_WEBHOOK_URL

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

def _send_to_discord(result: dict):
    payload = {
        "content": (
            f"**High Urgency Ticket!** \n\n"
            f"**Category:** {result['predicted_category']}\n"
            f"**Urgency Score:** {result['urgency_score']:.2f}\n"
            f"**Message:** {result['ticket_text']}"
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

def send_alert(ticket, score):
    """
    Single function your worker will call.
    """
    if MODE == "REAL":
        _send_to_discord(ticket, score)
    else:
        _send_to_mock(ticket, score)