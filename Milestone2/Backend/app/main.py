from fastapi import FastAPI
from celery.result import AsyncResult

from app.generator import TicketGenerator
from app.tasks import process_ticket_task
from app.celery_app import celery_app

app = FastAPI(title="Async Ticket Routing Engine")

CSV_PATH = "../../Final_customer_support_tickets.csv"


@app.get("/")
def root():
    return {"message": "Async Ticket Routing Engine Running"}


# ---------------------------------------------------
# AUTO GENERATE + SEND TO REDIS ON STARTUP
# ---------------------------------------------------
@app.on_event("startup")
def generate_and_dispatch():

    generator = TicketGenerator(CSV_PATH)

    tickets = generator.generate_random_tickets(10)

    print(f"Generated {len(tickets)} tickets. Sending to broker...")

    for ticket in tickets:
        task = process_ticket_task.delay(ticket.model_dump())
        print(f"Dispatched task: {task.id}")


# ---------------------------------------------------
# CHECK TASK STATUS
# ---------------------------------------------------
@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):

    result = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result
    }
generated_task_ids = []


@app.on_event("startup")
def generate_and_dispatch():

    generator = TicketGenerator(CSV_PATH)
    tickets = generator.generate_random_tickets(10)

    for ticket in tickets:
        task = process_ticket_task.delay(ticket.model_dump())
        generated_task_ids.append(task.id)

    print("Generated Task IDs:", generated_task_ids)
@app.get("/tasks")
def get_all_tasks():

    results = []

    for task_id in generated_task_ids:

        result = AsyncResult(task_id, app=celery_app)

        results.append({
            "task_id": task_id,
            "status": result.status,
            "result": result.result
        })

    return results