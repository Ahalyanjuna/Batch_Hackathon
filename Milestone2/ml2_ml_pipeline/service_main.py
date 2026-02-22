from fastapi import FastAPI
from pydantic import BaseModel
from ml2_ml_pipeline.inference import predict_ticket

app = FastAPI(title="ML Inference Service")


class TextInput(BaseModel):
    text: str


@app.get("/")
def root():
    return {"message": "ML Service Running"}


@app.post("/predict")
def predict(input: TextInput):
    result = predict_ticket(input.text)
    return result