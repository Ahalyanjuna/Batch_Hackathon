from pydantic import BaseModel

class ClassifyInput(BaseModel):
    subject: str
    description: str

class ClassifyOutput(BaseModel):
    category: str
    priority: str
    urgency_score: float
