from fastapi import FastAPI
from app.routers import chat, completions, admin
from app.services.metrics_collector import MetricsCollector
from app.utils.config_loader import ConfigLoader
import asyncio

# Load configuration
config_loader = ConfigLoader()
SERVERS = config_loader.get_models()
METRICS_UPDATE_INTERVAL = config_loader.get_metrics_update_interval()

# Initialize metrics collector
metrics_collector = MetricsCollector(SERVERS, update_interval=METRICS_UPDATE_INTERVAL)

# FastAPI app setup
app = FastAPI(title="LLMStream: Load Balanced LLM API")

# Include routers
app.include_router(chat.router, prefix="/v1/chat", tags=["Chat Completions"])
app.include_router(completions.router, prefix="/v1", tags=["Completions"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(metrics_collector.update_metrics())
    print("Metrics collector started")


@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
