import re


# -------------------------------
# Urgency Keyword Weights
# -------------------------------

HIGH_URGENCY_KEYWORDS = {
    "asap": 0.4,
    "urgent": 0.4,
    "immediately": 0.4,
    "critical": 0.5,
    "production down": 0.6,
    "server down": 0.6,
    "system failure": 0.6,
}

MEDIUM_URGENCY_KEYWORDS = {
    "error": 0.2,
    "failed": 0.2,
    "not working": 0.2,
    "issue": 0.15,
    "problem": 0.15,
}

LOW_URGENCY_KEYWORDS = {
    "clarification": 0.05,
    "inquiry": 0.05,
    "request": 0.05,
}


# -------------------------------
# Detect Urgency
# -------------------------------
def detect_urgency(text: str, subject_weight: float = 1.2) -> float:
    """
    Calculate urgency score based on keyword presence.

    Parameters:
    - text: combined subject + description
    - subject_weight: boost urgency if keyword appears in subject

    Returns:
    - urgency score between 0.0 and 1.0
    """

    if not text:
        return 0.0

    text = text.lower()

    score = 0.1  # base score

    # Check high urgency keywords
    for keyword, weight in HIGH_URGENCY_KEYWORDS.items():
        if re.search(rf"\b{re.escape(keyword)}\b", text):
            score += weight

    # Check medium urgency keywords
    for keyword, weight in MEDIUM_URGENCY_KEYWORDS.items():
        if re.search(rf"\b{re.escape(keyword)}\b", text):
            score += weight

    # Check low urgency keywords
    for keyword, weight in LOW_URGENCY_KEYWORDS.items():
        if re.search(rf"\b{re.escape(keyword)}\b", text):
            score += weight

    # Cap between 0 and 1
    return min(score, 1.0)