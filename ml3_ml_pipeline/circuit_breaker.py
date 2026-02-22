'''
 monitors ML2 latency, trips to ML1 fallback if >500ms for 3 consecutive requests, 
 resets when ML2 is healthy again.
 '''

import time
import pickle
import pandas as pd
from scipy.sparse import hstack
import re
import os

# ============================================================
# CIRCUIT BREAKER THRESHOLDS
# ============================================================
LATENCY_THRESHOLD_MS = 500   # failover if transformer > 500ms
FAILURE_COUNT_LIMIT   = 3    # failover after 3 consecutive failures

# State
_failure_count  = 0
_circuit_open   = False  # True = using fallback (ML1)

# ============================================================
# MILESTONE 1 FALLBACK — lightweight sklearn model
# ============================================================
ML1_MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ml1_models")

def _clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'[^a-zA-Z ]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def _ml1_predict(text: str) -> dict:
    """Milestone 1 fallback — fast sklearn TF-IDF + classifier."""
    with open(os.path.join(ML1_MODEL_DIR, "best_model.pkl"), "rb") as f:
        model = pickle.load(f)
    with open(os.path.join(ML1_MODEL_DIR, "subject_vectorizer.pkl"), "rb") as f:
        sub_vec = pickle.load(f)
    with open(os.path.join(ML1_MODEL_DIR, "content_vectorizer.pkl"), "rb") as f:
        des_vec = pickle.load(f)
    with open(os.path.join(ML1_MODEL_DIR, "label_encoder.pkl"), "rb") as f:
        le = pickle.load(f)

    clean = _clean_text(text)
    df = pd.DataFrame({"clean_subject": [clean], "description": [clean]})

    X = hstack([sub_vec.transform(df["clean_subject"]),
                des_vec.transform(df["description"])])

    pred = le.inverse_transform(model.predict(X))[0]

    return {
        "predicted_category": pred,
        "urgency_score":      0.5,   # ML1 has no urgency model
        "model_used":         "ML1-Fallback (sklearn)"
    }

# ============================================================
# CIRCUIT BREAKER WRAPPER
# ============================================================

def run_with_circuit_breaker(text: str, ml2_predict_fn) -> dict:
    """
    Tries ML2 transformer first.
    - If latency > 500ms OR failures >= 3 → failover to ML1.
    - Resets failure count on success.
    """
    global _failure_count, _circuit_open

    # If circuit already open, go straight to fallback
    if _circuit_open:
        print(f"  [CircuitBreaker] OPEN — using ML1 fallback")
        result = _ml1_predict(text)
        result["circuit_state"] = "OPEN"
        return result

    # Try ML2
    try:
        start = time.time()
        result = ml2_predict_fn(text)
        latency_ms = (time.time() - start) * 1000

        result["latency_ms"] = round(latency_ms, 2)

        if latency_ms > LATENCY_THRESHOLD_MS:
            _failure_count += 1
            print(f"  [CircuitBreaker] Latency {latency_ms:.0f}ms > {LATENCY_THRESHOLD_MS}ms "
                  f"(failure {_failure_count}/{FAILURE_COUNT_LIMIT})")

            if _failure_count >= FAILURE_COUNT_LIMIT:
                _circuit_open = True
                print(f"  [CircuitBreaker] TRIPPED — switching to ML1 fallback")

            # Failover this request too
            fallback = _ml1_predict(text)
            fallback["circuit_state"] = "HALF-OPEN"
            fallback["latency_ms"]    = round(latency_ms, 2)
            return fallback

        # Success — reset failure count
        _failure_count = 0
        result["model_used"]    = "ML2-Transformer"
        result["circuit_state"] = "CLOSED"
        return result

    except Exception as e:
        _failure_count += 1
        print(f"  [CircuitBreaker] ML2 error: {e} (failure {_failure_count}/{FAILURE_COUNT_LIMIT})")

        if _failure_count >= FAILURE_COUNT_LIMIT:
            _circuit_open = True

        fallback = _ml1_predict(text)
        fallback["circuit_state"] = "OPEN"
        return fallback


def reset_circuit():
    """Manually reset circuit breaker (call after ML2 is healthy again)."""
    global _failure_count, _circuit_open
    _failure_count = 0
    _circuit_open  = False
    print("  [CircuitBreaker] Reset — circuit CLOSED")