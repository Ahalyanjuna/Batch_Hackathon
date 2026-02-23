# Batch_Hackathon
 Hackathon Challenge: ”Smart-Support” Ticket Routing Engine
 # AI Ticket Classification & Urgency Detection System

An end-to-end FastAPI-based microservice system that classifies customer support tickets into categories and predicts urgency using NLP models.



---

## Features

* Ticket category classification (DistilBERT)
* Urgency score prediction
* Billing keyword override logic
* REST APIs using FastAPI
* Microservice architecture
* Latency tracking
* Label decoding via sklearn encoder

---

## Project Architecture

```
Milestone2/
│
├── Backend/
│   └── app/
│       ├── main.py
│       ├── tasks.py
│       └── services/
│           └── webhook.py
│
├── ML_Service/
│   └── app/
│       ├── main.py
│       ├── classifier.py
│       ├── urgency_model.py
│       └── saved_models/
│           ├── classifier/
│           │   ├── config.json
│           │   ├── pytorch_model.bin
│           │   ├── tokenizer.json
│           │   └── vocab.txt
│           └── label_encoder.pkl
│
└── README.md
```

---

##  ML Models Used

| Model                        | Purpose                        |
| ---------------------------- | ------------------------------ |
| DistilBERT                   | Ticket category classification |
| Regression / Sentiment model | Urgency scoring                |
| LabelEncoder                 | Category decoding              |

---

## Installation & Setup



### Install Dependencies

```bash
pip install fastapi uvicorn torch transformers scikit-learn requests
```


```bash
pip install torchvision torchaudio
```

---

## Running Services(For milesone 2 alone)

### 🔹 Start ML Service

From `Milestone2` root:

```bash
uvicorn ML_Service.app.main:app --reload --port 8001
```

ML API → http://127.0.0.1:8001

---

### 🔹 Start Backend Service

```bash
cd Backend
uvicorn app.main:app --reload --port 8000
```

Backend API → http://127.0.0.1:8000
```bash
cd Backend
celery -A app.celery_app worker --loglevel=info --pool=solo
```
---

## API Endpoint

### Classify Ticket

**POST** `/classify`

#### Request

```json
{
  "subject": "Payment deducted twice",
  "description": "Money was charged but order failed"
}
```

#### Response

```json
{
  "category": "Billing",
  "urgency_score": 0.82,
  "latency_seconds": 0.1432
}
```

---


## Model Paths

Configured in:

```
ML_Service/app/classifier.py
```

```python
CLASSIFIER_PATH = saved_models/classifier
LABEL_PATH = saved_models/label_encoder.pkl
```

Ensure these files exist before running.

---











