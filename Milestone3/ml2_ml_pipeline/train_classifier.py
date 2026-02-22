import os
import pandas as pd
import torch
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments
)

# -----------------------------
# 0. Create Required Directories
# -----------------------------
os.makedirs("saved_models", exist_ok=True)
os.makedirs("saved_models/classifier", exist_ok=True)

# -----------------------------
# 1. Load Dataset
# -----------------------------
df = pd.read_csv(
    r"C:\Users\user\Desktop\VSC Folder\Batch Hackathon\ml2_ml_pipeline\Final_customer_support_tickets.csv"
)

df = df.dropna(subset=["Ticket Description", "Ticket Type"])

texts = df["Ticket Description"].tolist()
labels = df["Ticket Type"].tolist()

print(f"Total samples: {len(texts)}")

# -----------------------------
# 2. Encode Labels
# -----------------------------
label_encoder = LabelEncoder()
encoded_labels = label_encoder.fit_transform(labels)

with open("saved_models/label_encoder.pkl", "wb") as f:
    pickle.dump(label_encoder, f)

print("Label encoder saved")

# -----------------------------
# 3. Train / Validation Split
# -----------------------------
X_train, X_val, y_train, y_val = train_test_split(
    texts,
    encoded_labels,
    test_size=0.2,
    random_state=42,
    stratify=encoded_labels
)

print(f"Training samples: {len(X_train)}")
print(f"Validation samples: {len(X_val)}")

# -----------------------------
# 4. Tokenization
# -----------------------------
tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")

train_encodings = tokenizer(
    X_train,
    truncation=True,
    padding=True,
    max_length=128
)

val_encodings = tokenizer(
    X_val,
    truncation=True,
    padding=True,
    max_length=128
)

# -----------------------------
# 5. Dataset Wrapper
# -----------------------------
class TicketDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

train_dataset = TicketDataset(train_encodings, y_train)
val_dataset = TicketDataset(val_encodings, y_val)

# -----------------------------
# 6. Model Initialization
# -----------------------------
model = DistilBertForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=len(label_encoder.classes_)
)

# -----------------------------
# 7. Training Configuration (COMPATIBLE)
# -----------------------------
training_args = TrainingArguments(
    output_dir="./saved_models/classifier",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_steps=50,
    load_best_model_at_end=True
)

# -----------------------------
# 8. Trainer
# -----------------------------
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset
)

# -----------------------------
# 9. Train Model
# -----------------------------
trainer.train()

# -----------------------------
# 10. Save Model & Tokenizer
# -----------------------------
trainer.save_model("saved_models/classifier")
tokenizer.save_pretrained("saved_models/classifier")

print(" Category classifier trained and saved successfully")