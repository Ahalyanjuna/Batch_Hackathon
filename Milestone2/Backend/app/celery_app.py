from celery import Celery

celery_app = Celery(
    "ticket_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

# tell celery where tasks are
celery_app.autodiscover_tasks(["app"])