from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from celery.result import AsyncResult
import threading
import time
from Backend.app.generator import TicketGenerator
from Backend.app.tasks import process_ticket_task
from Backend.app.celery_app import celery_app

app = FastAPI(title="Async Intelligent Queue System")

CSV_PATH = "../Final_customer_support_tickets.csv"
generator = TicketGenerator(CSV_PATH)

AUTO_BATCH_SIZE = 10        
AUTO_INTERVAL = 5           

@app.get("/")
def root():
    return {"message": "Async Intelligent Ticket Routing Engine Running"}


# ---------------------------------------------------
# BACKGROUND AUTO GENERATOR THREAD
# ---------------------------------------------------
def auto_generate_loop():
    """
    Runs forever in background.
    Generates tickets every few seconds and pushes to Celery.
    """
    while True:
        try:
            tickets = generator.generate_random_tickets(AUTO_BATCH_SIZE)

            print(f"\n Generating {len(tickets)} tickets...")

            for ticket in tickets:
                process_ticket_task.delay(ticket.model_dump())

        except Exception as e:
            print(" Generator Error:", e)

        time.sleep(AUTO_INTERVAL)


# ---------------------------------------------------
# START BACKGROUND THREAD WHEN APP STARTS
# ---------------------------------------------------
@app.on_event("startup")
def start_background_generator():
    thread = threading.Thread(target=auto_generate_loop, daemon=True)
    thread.start()
    print("Auto Ticket Generator Started")


# ---------------------------------------------------
# CHECK TASK STATUS (Optional debugging)
# ---------------------------------------------------
@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result
    }