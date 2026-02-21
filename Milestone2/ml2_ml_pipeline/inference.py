import time
import pickle
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

from urgency_model import get_urgency_score

# ============================================================
# 1. Load Category Classifier
# ============================================================
CLASSIFIER_PATH = "saved_models/classifier"

_cat_tokenizer = DistilBertTokenizer.from_pretrained(CLASSIFIER_PATH)
_cat_model     = DistilBertForSequenceClassification.from_pretrained(CLASSIFIER_PATH)
_cat_model.eval()

# ============================================================
# 2. Load Label Encoder
# ============================================================
with open("saved_models/label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

# ============================================================
# 3. Billing Override
# ============================================================
BILLING_KEYWORDS = [
    "payment", "invoice", "refund", "billing",
    "charged", "amount", "subscription", "upi", "card"
]

def override_category(text: str, predicted: str) -> str:
    if any(word in text.lower() for word in BILLING_KEYWORDS):
        return "Billing"
    return predicted

# ============================================================
# 4. Predict
# ============================================================
def predict_ticket(text: str) -> dict:
    start_time = time.time()

    # Step 1: Category classification
    cat_inputs = _cat_tokenizer(
        text,
        truncation=True,
        padding=True,
        max_length=128,
        return_tensors="pt"
    )
    with torch.no_grad():
        cat_outputs = _cat_model(**cat_inputs)
        pred_id = torch.argmax(cat_outputs.logits, dim=1).item()

    predicted_category = str(label_encoder.inverse_transform([pred_id])[0])
    final_category     = override_category(text, predicted_category)

    # Step 2: Urgency score from trained regression model
    urgency_score = get_urgency_score(text, final_category)

    latency = round(time.time() - start_time, 4)

    return {
        "ticket_text":        text,
        "predicted_category": final_category,
        "urgency_score":      urgency_score,
        "latency_seconds":    latency
    }

# ============================================================
# 5. Demo
# ============================================================
if __name__ == "__main__":
    test_tickets = [
        "Server down, production impacted badly",
        "I suspect a data breach has exposed my information tied to Fitbit Versa Smartwatch.",
        "Need invoice copy for accounting records",
        "UPI payment successful but order not confirmed",
        "There has been a violation of my consumer rights regarding the Sony PlayStation. I require immediate legal clarification and assistance."
    ]

    for ticket in test_tickets:
        print(predict_ticket(ticket))