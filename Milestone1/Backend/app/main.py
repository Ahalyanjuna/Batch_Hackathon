from fastapi import FastAPI, HTTPException
import httpx

from app.models import Ticket, TicketInput
from app.queue_manager import ticket_queue
from app.urgency import detect_urgency   # regex urgency

app = FastAPI(title="Ticket Routing Engine")

ML_SERVICE_URL = "http://localhost:8001/classify"


# ---------------------------
# ML service call
# ---------------------------
async def call_ml_service(subject: str, description: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                ML_SERVICE_URL,
                json={
                    "subject": subject,
                    "description": description
                },
                timeout=5.0
            )
            data = response.json()
            return data["category"], data["priority"], data["urgency_score"]
    except Exception:
        return "Technical", "low", 0.25


# ---------------------------
# Create ticket → Only Queue
# ---------------------------
@app.post("/tickets", status_code=201)
async def create_ticket(payload: TicketInput):

    # Assign temporary urgency using regex
    urgency_score = detect_urgency(
        payload.subject + " " + payload.description
    )

    ticket = Ticket(
        subject=payload.subject,
        description=payload.description,
        urgency_score=urgency_score
    )

    ticket_queue.push(ticket)

    return {
        "message": "Ticket queued successfully",
        "ticket_id": ticket.id,
        "current_queue_size": ticket_queue.size()
    }


# ---------------------------
# Process highest priority ticket
# ---------------------------
@app.get("/tickets/process")
async def process_next_ticket():

    if ticket_queue.is_empty():
        raise HTTPException(status_code=404, detail="No tickets in queue")

    # Pop highest priority
    ticket = ticket_queue.pop()

    # Now classify it
    category, priority, urgency_score = await call_ml_service(
        ticket.subject,
        ticket.description
    )

    ticket.category = category
    ticket.priority = priority
    ticket.urgency_score = urgency_score

    return {
        "message": "Ticket processed successfully",
        "ticket": ticket
    }


# ---------------------------
@app.get("/queue/size")
def get_queue_size():
    return {"size": ticket_queue.size()}