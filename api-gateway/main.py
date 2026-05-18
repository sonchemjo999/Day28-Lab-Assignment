# api-gateway/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator
import httpx, os, time

app = FastAPI(title="AI Platform API Gateway")
Instrumentator().instrument(app).expose(app)  # Integration 9: Prometheus

VLLM_URL = os.environ.get("VLLM_URL", "")
QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333")


class ChatRequest(BaseModel):
    query: str
    embedding: list[float] = [0.0] * 384


@app.post("/api/v1/chat")
async def chat(request: ChatRequest):
    start = time.time()

    # 1. Vector search (graceful fallback)
    context = []
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            search_resp = await client.post(f"{QDRANT_URL}/collections/documents/points/search", json={
                "vector": request.embedding,
                "limit": 3
            })
            if search_resp.status_code == 200:
                context = search_resp.json().get("result", [])
    except Exception:
        pass  # Fallback to empty context

    # 2. LLM inference
    prompt = f"Context: {context}\n\nQuery: {request.query}"
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            llm_resp = await client.post(f"{VLLM_URL}/v1/chat/completions", json={
                "model": "Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4",
                "messages": [{"role": "user", "content": prompt}]
            })
            llm_resp.raise_for_status()
            result = llm_resp.json()
            answer = result["choices"][0]["message"]["content"]
            model = result["model"]
    except Exception as e:
        return {
            "answer": f"LLM service unavailable: {str(e)[:100]}. Please ensure Kaggle vLLM is running.",
            "latency_ms": round((time.time() - start) * 1000, 2),
            "model": "unavailable"
        }

    latency = (time.time() - start) * 1000

    return {
        "answer": answer,
        "latency_ms": round(latency, 2),
        "model": model
    }

@app.get("/health")
def health():
    return {"status": "ok"}
