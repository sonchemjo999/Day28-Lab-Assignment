import requests, json

# Test 1: invalid request -> should return 422
resp = requests.post("http://localhost:8000/api/v1/chat", json={})
print(f"Test invalid request: {resp.status_code} - {resp.text}")

# Test 2: valid request -> check error
resp = requests.post("http://localhost:8000/api/v1/chat", json={
    "query": "What is AI?",
    "embedding": [0.1] * 384
}, timeout=30)
print(f"Test valid request: {resp.status_code} - {resp.text[:500]}")
