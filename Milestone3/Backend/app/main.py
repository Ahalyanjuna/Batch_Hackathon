from fastapi import FastAPI
from celery.result import AsyncResult

from app.generator import TicketGenerator
from app.tasks import process_ticket_task
from app.celery_app import celery_app

app = FastAPI(title="Async Ticket Routing Engine")

CSV_PATH = "../../Final_customer_support_tickets.csv"


@app.get("/")
def root():
    return {"message": "Backend Running"}


# -----------------------------------------
# GENERATE + DISPATCH TICKETS
# -----------------------------------------
@app.post("/tickets/generate/{count}")
def generate_tickets(count: int):

    generator = TicketGenerator(CSV_PATH)
    tickets = generator.generate_random_tickets(count)

    task_ids = []

    for ticket in tickets:
        task = process_ticket_task.delay(ticket.model_dump())
        task_ids.append(task.id)

    return {
        "message": f"{count} tickets sent for processing",
        "task_ids": task_ids
    }


# -----------------------------------------
# CHECK TASK STATUS
# -----------------------------------------
@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):

    result = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result
    }