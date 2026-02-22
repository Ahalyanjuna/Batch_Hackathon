from fastapi import FastAPI
from ML_Service.app.models import ClassifyInput, ClassifyOutput
from ML_Service.app.classifier import classify_ticket
from ML_Service.app.priority_map import map_priority

app = FastAPI(title="ML Classification Service")

@app.get("/")
def root():
    return {"message": "ML Service is running"}

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