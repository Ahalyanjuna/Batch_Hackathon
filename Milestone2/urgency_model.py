from transformers import pipeline

sentiment_model = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

def get_urgency_score(text: str, category: str = None) -> float:
    result = sentiment_model(text, truncation=True, max_length=128)[0]
    
    # POSITIVE confidence → low urgency, NEGATIVE confidence → high urgency
    if result["label"] == "NEGATIVE":
        raw = result["score"]          # e.g. 0.92 → high urgency
    else:
        raw = 1 - result["score"]      # e.g. 1 - 0.87 = 0.13 → low urgency

    # Category-aware baseline blend
    CATEGORY_BASELINE = {
        "Technical issue": 0.65,
        "Legal inquiry":   0.60,
        "Billing":         0.40,
        "General inquiry": 0.20,
    }

    if category and category in CATEGORY_BASELINE:
        baseline = CATEGORY_BASELINE[category]
        final = round(0.75 * raw + 0.25 * baseline, 3)
    else:
        final = round(raw, 3)

    return final