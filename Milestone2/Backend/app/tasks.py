import redis
from Backend.app.celery_app import celery_app
from ml2_ml_pipeline.inference import predict_ticket
from services.webhook import _send_to_discord

redis_client = redis.Redis(host="localhost", port=6379, db=0)


@celery_app.task(bind=True, max_retries=3)
def process_ticket_task(self, ticket_data: dict):

    lock_key = f"ticket_lock:{ticket_data['id']}"

    try:
        with redis_client.lock(lock_key, timeout=30):

            text = f"{ticket_data['subject']} {ticket_data['description']}"

            result = predict_ticket(text)

            if result["urgency_score"] > 0.7:
                _send_to_discord(result)

            return {
                "ticket_id": ticket_data["id"],
                "predicted_category": result["predicted_category"],
                "urgency_score": result["urgency_score"],
                "status": "COMPLETED"
            }

    except Exception as e:
        raise self.retry(exc=e, countdown=5)