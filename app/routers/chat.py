from fastapi import APIRouter, HTTPException, Request, Depends
from app.models.request import ChatCompletionRequest
from app.services.load_balancer import LoadBalancer
from app.services.logger import Logger
from app.utils.dependencies import get_load_balancer

router = APIRouter()
logger = Logger()

@router.post("/chat/completions")  # 상대 경로
async def chat_completions(
    request: Request,
    payload: ChatCompletionRequest,
    load_balancer: LoadBalancer = Depends(get_load_balancer)
):
    """
    Chat Completions API 엔드포인트.
    - 요청을 적절한 서버로 라우팅.
    """
    model_name = payload.model

    # 모델 이름이 제공되지 않은 경우 예외 처리
    if not model_name:
        raise HTTPException(status_code=400, detail="Model name must be specified.")

    # 로드 밸런서를 통해 서버 선택
    selected_server = await load_balancer.select_server(model_name)
    if not selected_server:
        raise HTTPException(status_code=503, detail="No available servers for the model.")

    # 헤더 및 페이로드 준비
    headers = dict(request.headers)
    try:
        # 요청 전달
        response = await load_balancer.forward_request(
            f"{selected_server}/v1/chat/completions", payload.dict(), headers
        )
        logger.log_request(payload, response)
        return response
    except RuntimeError as e:
        logger.log_error(payload, str(e))
        raise HTTPException(status_code=502, detail=f"Error contacting server: {str(e)}")
