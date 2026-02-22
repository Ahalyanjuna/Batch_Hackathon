import time
import pickle
import torch
import numpy as np
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

from urgency_model import get_urgency_score


# -----------------------------
# 1. Load Trained Classifier
# -----------------------------
MODEL_PATH = "saved_models/classifier"

tokenizer = DistilBertTokenizer.from_pretrained(MODEL_PATH)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

# -----------------------------
# 2. Load Label Encoder
# -----------------------------
with open("saved_models/label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

# -----------------------------
# 3. Billing Override Logic
# -----------------------------
BILLING_KEYWORDS = [
    "payment", "invoice", "refund", "billing",
    "charged", "amount", "subscription", "upi", "card"
]

def override_category(text, predicted):
    text_l = text.lower()
    if any(word in text_l for word in BILLING_KEYWORDS):
        return "Billing"
    return predicted

# -----------------------------
# 4. Inference Function
# -----------------------------
def predict_ticket(text: str):
    start_time = time.time()

    inputs = tokenizer(
        text,
        truncation=True,
        padding=True,
        max_length=128,
        return_tensors="pt"
    )

    with torch.no_grad():
        outputs = model(**inputs)
        pred_id = torch.argmax(outputs.logits, dim=1).item()

    predicted_category = str(
        label_encoder.inverse_transform([pred_id])[0]
    )

    # Apply override
    final_category = override_category(text, predicted_category)

    # Urgency score
    urgency_score = get_urgency_score(text)

    latency = round(time.time() - start_time, 4)

    return {
        "ticket_text": text,
        "predicted_category": final_category,
        "urgency_score": urgency_score,
        "latency_seconds": latency
    }

# -----------------------------
# 5. Demo Testing
# -----------------------------
if __name__ == "__main__":
    test_tickets = [
        "Server down, production impacted badly",
        "I suspect a data breach has exposed my information tied to Fitbit Versa Smartwatch.",
        "Need invoice copy for accounting records",
        "UPI payment successful but order not confirmed"
    ]

    for t in test_tickets:
        print(predict_ticket(t))