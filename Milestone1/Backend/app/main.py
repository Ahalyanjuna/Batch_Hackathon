from fastapi import FastAPI, HTTPException
import httpx
from models import Ticket, TicketInput
from queue_manager import ticket_queue

app = FastAPI(title="Ticket Routing Engine")

ML_SERVICE_URL = "http://localhost:8001/classify"

async def call_ml_service(subject: str, description: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(ML_SERVICE_URL, json={
                "subject": subject,
                "description": description
            }, timeout=5.0)
            data = response.json()
            return data["category"], data["priority"], data["urgency_score"]
    except Exception:
        # Fallback if ML service is down
        return "Technical", "low", 0.25


@app.post("/tickets", status_code=201)
async def create_ticket(payload: TicketInput):
    # Call ML service for classification
    category, priority, urgency_score = await call_ml_service(
        payload.subject, payload.description
    )

    # Create full Ticket object
    ticket = Ticket(
        subject=payload.subject,
        description=payload.description,
        category=category,
        priority=priority,
        urgency_score=urgency_score
    )

    # Push to priority queue
    ticket_queue.push(ticket)

    return {
        "message": "Ticket created successfully",
        "ticket_id": ticket.id,
        "category": ticket.category,
        "priority": ticket.priority,
        "urgency_score": ticket.urgency_score
    }


@app.get("/tickets/next")
def get_next_ticket():
    if ticket_queue.is_empty():
        raise HTTPException(status_code=404, detail="No tickets in queue")
    
    ticket = ticket_queue.pop()
    return ticket


@app.get("/tickets")
def get_all_tickets():
    if ticket_queue.is_empty():
        raise HTTPException(status_code=404, detail="Queue is empty")
    
    return {
        "total": ticket_queue.size(),
        "tickets": ticket_queue.all_tickets()
    }


@app.get("/queue/size")
def get_queue_size():
    return {"size": ticket_queue.size()}