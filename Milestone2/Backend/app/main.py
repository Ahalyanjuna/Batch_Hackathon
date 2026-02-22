from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from celery.result import AsyncResult

from Backend.app.generator import TicketGenerator
from Backend.app.tasks import process_ticket_task
from Backend.app.celery_app import celery_app

app = FastAPI(title="Async Intelligent Queue System")

CSV_PATH = "../../Final_customer_support_tickets.csv"
generator = TicketGenerator(CSV_PATH)


@app.get("/")
def root():
    return {"message": "Async Intelligent Ticket Routing Engine Running"}


# ---------------------------------------------------
# CREATE TICKET (Returns 202 Immediately)
# ---------------------------------------------------
@app.post("/tickets", status_code=202)
def create_ticket():

    ticket = generator.generate_random_tickets(1)[0]

    task = process_ticket_task.delay(ticket.model_dump())

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "message": "Ticket accepted for processing",
            "task_id": task.id
        }
    )


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