import os
import re
import torch
import pandas as pd
from torch import nn
from sklearn.model_selection import train_test_split
from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments
)
from torch.utils.data import Dataset

URGENCY_MODEL_PATH = "saved_models/urgency_regressor"

PRIORITY_MAP = {
    "Low":      0.1,
    "Medium":   0.4,
    "High":     0.75,
    "Critical": 1.0,
}

# Keywords that strongly signal high urgency
HIGH_URGENCY_KEYWORDS = [
    "down", "outage", "breach", "hack", "exposed", "immediate",
    "critical", "urgent", "production", "impacted", "legal",
    "violation", "lawsuit", "fraud", "stolen", "unauthorized",
    "emergency", "failed", "not working", "crashed", "data loss"
]

# Keywords that signal low urgency
LOW_URGENCY_KEYWORDS = [
    "invoice copy", "accounting", "records", "information",
    "question", "inquiry", "how to", "update", "change",
    "general", "feedback", "suggestion", "thank"
]

# ============================================================
# PART 1 — DATASET
# ============================================================

class UrgencyDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels    = labels

    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx], dtype=torch.float)
        return item

    def __len__(self):
        return len(self.labels)


# ============================================================
# PART 2 — CUSTOM TRAINER
# ============================================================

class RegressionTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        predictions = torch.sigmoid(outputs.logits.squeeze(-1))
        loss = nn.MSELoss()(predictions, labels)
        return (loss, outputs) if return_outputs else loss


# ============================================================
# PART 3 — TRAINING FUNCTION
# ============================================================

def train_urgency_model(csv_path: str):
    os.makedirs(URGENCY_MODEL_PATH, exist_ok=True)

    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["Ticket Description", "Ticket Priority"])
    df["Ticket Priority"] = df["Ticket Priority"].str.strip().str.capitalize()
    df = df[df["Ticket Priority"].isin(PRIORITY_MAP)]
    df["urgency_score"] = df["Ticket Priority"].map(PRIORITY_MAP)

    print(f"Total samples      : {len(df)}")
    print(f"Priority distribution:\n{df['Ticket Priority'].value_counts()}\n")

    texts  = df["Ticket Description"].tolist()
    labels = df["urgency_score"].tolist()

    X_train, X_val, y_train, y_val = train_test_split(
        texts, labels, test_size=0.2, random_state=42
    )

    tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
    train_enc = tokenizer(X_train, truncation=True, padding=True, max_length=128)
    val_enc   = tokenizer(X_val,   truncation=True, padding=True, max_length=128)

    train_dataset = UrgencyDataset(train_enc, y_train)
    val_dataset   = UrgencyDataset(val_enc,   y_val)

    model = DistilBertForSequenceClassification.from_pretrained(
        "distilbert-base-uncased",
        num_labels=1,
    )

    training_args = TrainingArguments(
        output_dir=URGENCY_MODEL_PATH,
        num_train_epochs=4,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        logging_steps=50,
        fp16=torch.cuda.is_available(),
    )

    trainer = RegressionTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
    )

    trainer.train()
    trainer.save_model(URGENCY_MODEL_PATH)
    tokenizer.save_pretrained(URGENCY_MODEL_PATH)
    print("\nUrgency regression model trained and saved successfully")


# ============================================================
# PART 4 — KEYWORD SIGNAL (calibration layer)
# ============================================================

def _keyword_signal(text: str) -> float:
    """
    Returns a signal in [0, 1] based on urgency keyword presence.
    Acts as a calibration layer on top of the regression model output.
    """
    text_l = text.lower()

    high_hits = sum(1 for kw in HIGH_URGENCY_KEYWORDS if kw in text_l)
    low_hits  = sum(1 for kw in LOW_URGENCY_KEYWORDS  if kw in text_l)

    if high_hits == 0 and low_hits == 0:
        return 0.5  # neutral

    total = high_hits + low_hits
    return round(high_hits / total, 3)


# ============================================================
# PART 5 — INFERENCE FUNCTION
# ============================================================

_tokenizer = None
_model     = None

def _load_model():
    global _tokenizer, _model
    if _model is None:
        _tokenizer = DistilBertTokenizer.from_pretrained(URGENCY_MODEL_PATH)
        _model     = DistilBertForSequenceClassification.from_pretrained(URGENCY_MODEL_PATH)
        _model.eval()


def get_urgency_score(text: str, category: str = None) -> float:
    """
    Hybrid urgency score in [0, 1]:
    - 60% from trained DistilBERT regression model
    - 40% from keyword calibration signal
    This ensures meaningful score differentiation even when
    the regression model output is flat due to dataset limitations.
    """
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
        model_score = torch.sigmoid(outputs.logits.squeeze(-1)).item()

    keyword_score = _keyword_signal(text)

    # Weighted blend
    final = 0.6 * model_score + 0.4 * keyword_score

    return round(float(min(max(final, 0.0), 1.0)), 3)


# ============================================================
# PART 6 — TRAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    CSV_PATH = r"C:\Users\user\Desktop\VSC Folder\Batch Hackathon\ml2_ml_pipeline\Final_customer_support_tickets.csv"
    train_urgency_model(CSV_PATH)