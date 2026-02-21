from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Mock Webhook Service")

class MockPayload(BaseModel):
    id: int
    category: str
    score: float
    message: str

@app.post("/mock_webhook/slack")
def mock_slack(payload: MockPayload):
    # This simulates Slack receiving a webhook
    print("\n🚨 MOCK SLACK ALERT RECEIVED")
    print({
        "id": payload.id,
        "category": payload.category,
        "score": payload.score,
        "message": payload.message
    })
    return {"status": "received"}