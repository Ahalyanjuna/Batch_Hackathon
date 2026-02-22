import time
import pickle
import torch
import os
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

from app.urgency_model import get_urgency_score


# ----------------------------------
# 1. Paths
# ----------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLASSIFIER_PATH = os.path.join(BASE_DIR, "saved_models", "classifier")
LABEL_PATH = os.path.join(BASE_DIR, "saved_models", "label_encoder.pkl")

with open(LABEL_PATH, "rb") as f:
    label_encoder = pickle.load(f)


# ----------------------------------
# 2. Load Model + Tokenizer (ONCE)
# ----------------------------------

tokenizer = DistilBertTokenizer.from_pretrained(CLASSIFIER_PATH)
model = DistilBertForSequenceClassification.from_pretrained(CLASSIFIER_PATH)

model.eval()


# ----------------------------------
# 3. Load Label Encoder
# ----------------------------------

with open(LABEL_ENCODER_PATH, "rb") as f:
    label_encoder = pickle.load(f)


# ----------------------------------
# 4. Billing Override Logic
# ----------------------------------

BILLING_KEYWORDS = [
    "payment", "invoice", "refund", "billing",
    "charged", "amount", "subscription", "upi", "card"
]


def override_category(text, predicted):
    text_l = text.lower()

    if any(word in text_l for word in BILLING_KEYWORDS):
        return "Billing"

    return predicted


# ----------------------------------
# 5. Main Inference Function
# ----------------------------------

def classify_ticket(subject: str, description: str):

    start_time = time.time()

    text = subject + " " + description

    # Tokenize
    inputs = tokenizer(
        text,
        truncation=True,
        padding=True,
        max_length=128,
        return_tensors="pt"
    )

    # Model inference
    with torch.no_grad():
        outputs = model(**inputs)
        pred_id = torch.argmax(outputs.logits, dim=1).item()

    predicted_category = str(
        label_encoder.inverse_transform([pred_id])[0]
    )

    # Billing override
    final_category = override_category(text, predicted_category)

    # Urgency score (from regressor / sentiment model)
    urgency_score = get_urgency_score(text)

    latency = round(time.time() - start_time, 4)

    return {
        "category": final_category,
        "urgency_score": urgency_score,
        "latency_seconds": latency
    }