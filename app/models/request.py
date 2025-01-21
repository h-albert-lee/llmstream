from pydantic import BaseModel
from typing import List, Optional


class CompletionRequest(BaseModel):
    model: str
    prompt: str
    max_tokens: int
    temperature: Optional[float] = 1.0
    stream: Optional[bool] = False  # 스트리밍 여부 추가
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stop: Optional[List[str]] = None

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[dict]
    max_tokens: Optional[int] = 100
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False  # 스트리밍 여부 추가
    repetition_penalty: Optional[float] = 1.0
    presence_penalty: Optional[float] = 0.0
