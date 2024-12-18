from pydantic import BaseModel
from typing import List, Optional

class CompletionRequest(BaseModel):
    model: str
    prompt: str
    max_tokens: int
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stop: Optional[List[str]] = None

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[dict]
    max_tokens: int
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stop: Optional[List[str]] = None
