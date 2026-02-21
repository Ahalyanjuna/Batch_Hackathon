from fastapi import FastAPI, HTTPException
import httpx

from app.models import Ticket, TicketInput
from app.queue_manager import ticket_queue
from app.urgency import detect_urgency
from app.generator import TicketGenerator

app = FastAPI(title="Ticket Routing Engine")

ML_SERVICE_URL = "http://localhost:8001/classify"

# Dataset path
CSV_PATH = "../../Final_customer_support_tickets.csv"


@app.get("/")
def root():
    return {"message": "Ticket Routing Engine Running"}


# ---------------------------------------------------
# AUTO SEED QUEUE ON STARTUP 
# ---------------------------------------------------
@app.on_event("startup")
def seed_queue_on_startup():
    try:
        generator = TicketGenerator(CSV_PATH)
        tickets = generator.generate_random_tickets(10)
        generator.push_to_queue(tickets)
        print(f"Seeded {len(tickets)} tickets")
    except Exception as e:
        print("Startup seeding failed:", e)

# ---------------------------------------------------
# ML SERVICE CALL
# ---------------------------------------------------
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
        # fallback if ML service is down
        return "Technical", "low", 0.25


# ---------------------------------------------------
# CREATE TICKET → QUEUE ONLY
# ---------------------------------------------------
@app.post("/tickets", status_code=201)
async def create_ticket(payload: TicketInput):

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


# ---------------------------------------------------
# GENERATE RANDOM TICKETS FROM CSV (FOR TESTING)
# ---------------------------------------------------
@app.post("/tickets/generate/{count}")
def generate_tickets(count: int):
    generator = TicketGenerator(CSV_PATH)

    tickets = generator.generate_random_tickets(count)
    generator.push_to_queue(tickets)

    return {
        "message": f"{count} tickets generated and added to queue",
        "queue_size": ticket_queue.size()
    }


# ---------------------------------------------------
# PROCESS HIGHEST PRIORITY TICKET
# ---------------------------------------------------
@app.get("/tickets/process")
async def process_next_ticket():

    if ticket_queue.is_empty():
        raise HTTPException(status_code=404, detail="No tickets in queue")

    # pop highest urgency ticket
    ticket = ticket_queue.pop()

    # call ML classifier service
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


# ---------------------------------------------------
# QUEUE SIZE
# ---------------------------------------------------
@app.get("/queue/size")
def get_queue_size():
    return {"size": ticket_queue.size()}