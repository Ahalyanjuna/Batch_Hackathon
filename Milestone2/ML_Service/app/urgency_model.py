import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
URGENCY_MODEL_PATH = os.path.join(
    BASE_DIR,
    "saved_models",
    "urgency_regressor"
)

_tokenizer = None
_model = None


def _load_model():
    global _tokenizer, _model

    if _model is None:
        _tokenizer = DistilBertTokenizer.from_pretrained(URGENCY_MODEL_PATH)
        _model = DistilBertForSequenceClassification.from_pretrained(URGENCY_MODEL_PATH)
        _model.eval()


def get_urgency_score(text: str) -> float:

    _load_model()

    inputs = _tokenizer(
        text,
        truncation=True,
        padding=True,
        max_length=128,
        return_tensors="pt"
    )

    with torch.no_grad():
        outputs = _model(**inputs)
        score = torch.sigmoid(outputs.logits.squeeze(-1)).item()

    return round(float(score), 3)