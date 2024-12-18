from fastapi import APIRouter, HTTPException, Request
from app.models.request import ChatCompletionRequest
from app.services.load_balancer import LoadBalancer
from app.services.logger import Logger

router = APIRouter()
logger = Logger()
load_balancer = LoadBalancer(metrics_collector, config_loader)


@router.post("/completions")
async def chat_completions(request: Request, payload: ChatCompletionRequest):
    model_name = payload.model

    # 서버 선택
    selected_server = await load_balancer.select_server(model_name)
    if not selected_server:
        raise HTTPException(
            status_code=503, detail="No available servers for the model"
        )

    # 헤더 포함하여 요청 전달
    headers = dict(request.headers)
    try:
        response = await load_balancer.forward_request(
            f"{selected_server}/v1/chat/completions", payload.dict(), headers
        )
        logger.log_request(payload, response)
        return response
    except RuntimeError as e:
        logger.log_error(payload, str(e))
        raise HTTPException(
            status_code=502, detail=f"Error contacting server: {str(e)}"
        )
