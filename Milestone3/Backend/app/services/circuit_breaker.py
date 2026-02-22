

import time
import httpx

FAILURE_THRESHOLD = 3
LATENCY_THRESHOLD = 0.5  # 500ms

failure_count = 0
circuit_open = False

ML2_URL = "http://localhost:8001/classify"
ML1_URL = "http://localhost:8001/classify-fallback"  # optional


async def classify_with_circuit_breaker(subject, description):
    global failure_count, circuit_open

    text_payload = {
        "subject": subject,
        "description": description
    }

    if circuit_open:
        return await call_fallback(text_payload)

    try:
        start = time.time()

        async with httpx.AsyncClient() as client:
            response = await client.post(ML2_URL, json=text_payload)

        latency = time.time() - start

        if latency > LATENCY_THRESHOLD:
            failure_count += 1
        else:
            failure_count = 0

        if failure_count >= FAILURE_THRESHOLD:
            circuit_open = True
            return await call_fallback(text_payload)

        return response.json()

    except Exception:
        failure_count += 1
        if failure_count >= FAILURE_THRESHOLD:
            circuit_open = True
        return await call_fallback(text_payload)


async def call_fallback(payload):
    async with httpx.AsyncClient() as client:
        response = await client.post(ML2_URL, json=payload)
    return response.json()