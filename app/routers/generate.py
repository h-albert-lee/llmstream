from fastapi import APIRouter, HTTPException, Request, Depends
from app.services.load_balancer import LoadBalancer
from app.services.logger import Logger
from app.utils.dependencies import get_load_balancer

router = APIRouter()
logger = Logger()

@router.post("/generate")  # 상대 경로로 설정
async def generate(
    request: Request,
    load_balancer: LoadBalancer = Depends(get_load_balancer)
):
    """
    Generate API 엔드포인트.
    - 모든 요청을 기본 서버로 전달.
    """
    # 로드 밸런서를 통해 기본 서버 선택
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
