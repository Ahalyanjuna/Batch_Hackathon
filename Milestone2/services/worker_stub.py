import random
from services.webhook import send_alert

def fake_classifier(text):
    # simulate category
    if "bill" in text.lower():
        return "Billing"
    if "legal" in text.lower():
        return "Legal"
    return "Technical"

def fake_urgency_score(text):
    # simple heuristic to simulate your transformer output
    keywords = ["broken", "down", "asap", "urgent", "immediately", "production"]
    base = 0.3
    for k in keywords:
        if k in text.lower():
            base += 0.15
    return min(base, 0.99)

def process_ticket(ticket):
    category = fake_classifier(ticket["text"])
    score = fake_urgency_score(ticket["text"])

    ticket["category"] = category

    print(f"Processed Ticket {ticket['id']} → category={category}, score={score:.2f}")

    if score > 0.7:
        send_alert(ticket, score)

if __name__ == "__main__":
    # simulate a burst of tickets
    samples = [
        {"id": 1, "text": "My system is broken and production is down ASAP"},
        {"id": 2, "text": "Need invoice copy for last month bill"},
        {"id": 3, "text": "Service degraded, urgent assistance required immediately"},
        {"id": 4, "text": "Production system broken urgent asap immediately down"}
    ]
    for t in samples:
        process_ticket(t)