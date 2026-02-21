from fastapi import FastAPI
from app.models import ClassifyInput, ClassifyOutput
from app.classifier import classify_category

app = FastAPI(title="ML Classification Service")


@app.post("/classify", response_model=ClassifyOutput)
def classify(payload: ClassifyInput):

    text = payload.subject + " " + payload.description

    # Category prediction
    category = classify_category(text)

    return ClassifyOutput(
        category=category
    )