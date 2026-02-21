# just dummy


def detect_urgency(text: str) -> float:
    """
    Keyword-based urgency scoring.
    Replace with sentiment model later.
    """

    keywords = ["asap", "urgent", "immediately", "error", "failure"]

    score = 0.2

    for word in keywords:
        if word in text.lower():
            score += 0.2

    return min(score, 1.0)