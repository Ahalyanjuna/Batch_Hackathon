def map_priority(score: float) -> str:

    if score >= 0.85:
        return "Critical"
    elif score >= 0.6:
        return "High"
    elif score >= 0.35:
        return "Medium"
    else:
        return "Low"