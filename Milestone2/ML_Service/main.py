from fastapi import FastAPI
from Backend.app.models import ClassifyInput, ClassifyOutput
from ML_Service.classifier import classify_category

app = FastAPI(title="ML Classification Service")


@app.post("/classify", response_model=ClassifyOutput)
def classify(payload: ClassifyInput):
    # Category prediction
    category = classify_category(payload.subject, payload.description)

    return ClassifyOutput(
        category=category
    )