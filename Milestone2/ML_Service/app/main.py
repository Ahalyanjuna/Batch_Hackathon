from fastapi import FastAPI
from app.models import ClassifyInput, ClassifyOutput
from app.classifier import classify_ticket
from app.priority_map import map_priority

app = FastAPI(title="ML Classification Service")


@app.post("/classify", response_model=ClassifyOutput)
def classify(payload: ClassifyInput):

    result = classify_ticket(
        payload.subject,
        payload.description
    )

    priority = map_priority(result["urgency_score"])

    return ClassifyOutput(
        category=result["category"],
        priority=priority,
        urgency_score=result["urgency_score"]
    )