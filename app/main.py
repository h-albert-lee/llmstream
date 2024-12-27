from fastapi import FastAPI, Depends
from app.routers import chat, generate, completions
from app.services.load_balancer import LoadBalancer
from app.services.metrics_collector import MetricsCollector
from app.utils.config_loader import ConfigLoader
import asyncio

# 전역적으로 초기화된 의존성
config_loader = ConfigLoader("config.json")
server_dict = {model_name: model["servers"] for model_name, model in config_loader.config["models"].items()}
metrics_collector = MetricsCollector(servers=server_dict)  # 딕셔너리 전달
load_balancer = LoadBalancer(metrics_collector, config_loader)

# FastAPI 앱 생성
app = FastAPI()

# 백그라운드 작업 추적
background_tasks = []

# 의존성 제공 함수
def get_load_balancer():
    return load_balancer

# 라우터 등록
app.include_router(chat.router, prefix="/v1", tags=["chat"], dependencies=[Depends(get_load_balancer)])
app.include_router(generate.router, prefix="", tags=["generate"], dependencies=[Depends(get_load_balancer)])
app.include_router(completions.router, prefix="/v1", tags=["completions"], dependencies=[Depends(get_load_balancer)])

@app.on_event("startup")
async def startup_event():
    task = asyncio.create_task(metrics_collector.update_metrics())
    background_tasks.append(task)
    print("Metrics collector started")

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down...")
    for task in background_tasks:
        task.cancel()
    await asyncio.gather(*background_tasks, return_exceptions=True)
