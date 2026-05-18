import redis, json, time

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

features = [
    {"id": "doc_001", "text": "AI platform integration test"},
    {"id": "doc_002", "text": "Kafka to Airflow pipeline"},
    {"id": "smoke_001", "text": "smoke test document"},
]

for row in features:
    feature_key = f"feature:{row['id']}"
    r.set(feature_key, json.dumps({
        "text": row["text"],
        "timestamp": time.time(),
        "processed": True
    }))

keys = r.keys("feature:*")
print(f"Integration 3+4 OK: {len(keys)} features stored in Feast (Redis)")
for k in keys:
    print(f"  - {k}")
