from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# load lightweight model
model = SentenceTransformer("all-MiniLM-L6-v2")

# in-memory buffer
recent_tickets = []

# config
TIME_WINDOW_MINUTES = 5
SIMILARITY_THRESHOLD = 0.9
STORM_COUNT_THRESHOLD = 10


def _clean_old():
    """
    Remove tickets older than 5 minutes
    """
    global recent_tickets
    cutoff = datetime.utcnow() - timedelta(minutes=TIME_WINDOW_MINUTES)
    recent_tickets = [t for t in recent_tickets if t["time"] > cutoff]


def check_ticket_storm(ticket_text: str):
    """
    Returns:
        (is_storm: bool, cluster_size: int)
    """
    global recent_tickets

    _clean_old()

    # embed incoming ticket
    emb = model.encode([ticket_text])[0]

    similar_count = 0

    for t in recent_tickets:
        sim = cosine_similarity([emb], [t["embedding"]])[0][0]
        if sim > SIMILARITY_THRESHOLD:
            similar_count += 1

    # store current ticket
    recent_tickets.append({
        "embedding": emb,
        "time": datetime.utcnow()
    })

    if similar_count >= STORM_COUNT_THRESHOLD:
        print("**Tickets are similar**")
        return True, similar_count + 1
    else:
        return False, similar_count + 1