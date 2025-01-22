from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from app.models.request import ChatCompletionRequest
from app.services.load_balancer import LoadBalancer
from app.services.logger import Logger
from app.utils.dependencies import get_load_balancer

router = APIRouter()
logger = Logger()

@router.post("/chat/completions")
async def chat_completions(
    request: Request,
    payload: ChatCompletionRequest,
    load_balancer: LoadBalancer = Depends(get_load_balancer)
):
    model_name = payload.model
    stream = payload.stream

    if not model_name:
        raise HTTPException(status_code=400, detail="Model name must be specified.")

    selected_server = await load_balancer.select_server(model_name)
    if not selected_server:
        raise HTTPException(status_code=503, detail="No available servers for the model.")

    headers = dict(request.headers)
    try:
        response = await load_balancer.forward_request(
            f"{selected_server}/v1/chat/completions", payload.dict(), headers, stream=stream
        )

        if stream:
            async def stream_generator():
                async for chunk in response:
                    yield chunk

            return StreamingResponse(stream_generator(), media_type="application/json")
        else:
            return response
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=f"Error contacting server: {str(e)}")
