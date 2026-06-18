from fastapi import APIRouter, Response
from prometheus_client import generate_latest, Counter, Histogram, REGISTRY
import time

router = APIRouter(tags=["health"])

REQUEST_COUNT = Counter("app_requests_total", "Total requests")
REQUEST_LATENCY = Histogram("app_request_latency_seconds", "Request latency")


@router.get("/health")
async def health_check():
    REQUEST_COUNT.inc()
    start = time.time()
    result = {"status": "healthy", "service": "ai-agent-shop"}
    REQUEST_LATENCY.observe(time.time() - start)
    return result


@router.get("/metrics")
async def metrics():
    return Response(content=generate_latest(REGISTRY), media_type="text/plain")
