import time
import pickle
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from ml2_ml_pipeline.urgency_model import get_urgency_score

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

CLASSIFIER_PATH = "saved_models/classifier"

_cat_tokenizer = DistilBertTokenizer.from_pretrained(CLASSIFIER_PATH)
_cat_model = DistilBertForSequenceClassification.from_pretrained(CLASSIFIER_PATH)
_cat_model.to(DEVICE)
_cat_model.eval()

with open("saved_models/label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

BILLING_KEYWORDS = [
    "payment", "invoice", "refund", "billing",
    "charged", "amount", "subscription", "upi", "card"
]

def override_category(text: str, predicted: str) -> str:
    if any(word in text.lower() for word in BILLING_KEYWORDS):
        return "Billing"
    return predicted


def predict_ticket(text: str) -> dict:
    start_time = time.time()

    inputs = _cat_tokenizer(
        text,
        truncation=True,
        padding=True,
        max_length=128,
        return_tensors="pt"
    ).to(DEVICE)

    with torch.no_grad():
        outputs = _cat_model(**inputs)
        pred_id = torch.argmax(outputs.logits, dim=1).item()

    predicted_category = str(label_encoder.inverse_transform([pred_id])[0])
    final_category = override_category(text, predicted_category)

    urgency_score = float(get_urgency_score(text, final_category))

    latency = round(time.time() - start_time, 4)

    return {
        "ticket_text": text,
        "predicted_category": final_category,
        "urgency_score": urgency_score,
        "latency_seconds": latency
    }