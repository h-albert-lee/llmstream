from fastapi import APIRouter, HTTPException, Request
from app.services.load_balancer import LoadBalancer
from app.services.logger import Logger

router = APIRouter()
logger = Logger()
load_balancer = LoadBalancer(metrics_collector, config_loader)

@router.post("/generate")
async def generate(request: Request):
    # /generate는 기본 서버로 라우팅
    selected_server = await load_balancer.select_server(is_generate=True)
    if not selected_server:
        raise HTTPException(status_code=503, detail="No available server for /generate requests")

    # 요청 전달
    headers = dict(request.headers)
    payload = await request.json()
    try:
        response = await load_balancer.forward_request(f"{selected_server}/generate", payload, headers)
        logger.log_request(payload, response)
        return response
    except RuntimeError as e:
        logger.log_error(payload, str(e))
        raise HTTPException(status_code=502, detail=f"Error contacting server: {str(e)}")
