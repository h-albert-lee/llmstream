from fastapi import APIRouter, HTTPException
from app.models.request import CompletionRequest
from app.services.load_balancer import LoadBalancer
from app.services.logger import Logger

router = APIRouter()
logger = Logger()
load_balancer = LoadBalancer(metrics_collector, config_loader)

@router.post("/completions")
async def completions(request: CompletionRequest):
    model_name = request.model

    # 모델별 로드 밸런싱 전략 적용
    selected_server = await load_balancer.select_server(model_name)
    if not selected_server:
        raise HTTPException(status_code=503, detail="No available servers for the model")

    # 요청 전달
    try:
        response = await load_balancer.forward_request(
            f"{selected_server}/v1/completions", request.dict()
        )
        logger.log_request(request, response)
        return response
    except Exception as e:
        logger.log_error(request, str(e))
        raise HTTPException(status_code=502, detail=f"Error contacting server: {str(e)}")
