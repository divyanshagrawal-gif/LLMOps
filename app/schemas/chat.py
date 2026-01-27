from pydantic import BaseModel

class ChatRequest(BaseModel):
    prompt: str
    temperature: float = 0.7
    max_tokens: int = 1024

class ChatResponse(BaseModel):
    response: str
    model: str
    latency: float
    cache_hit: bool
