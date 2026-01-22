from fastapi import APIRouter, Request
from app.schemas.chat import ChatRequest, ChatResponse
from fastapi.responses import StreamingResponse
from app.services.gemini_client import GeminiClient

router = APIRouter()
client = GeminiClient()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, req: Request):
    result = client.generate(
        prompt=request.prompt,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        request_id=req.state.request_id
    )

    return ChatResponse(
        response=result["text"],
        model=result["model"],
        latency=result["latency"]
    )

@router.post("/chat/stream")
def chat_stream(request: ChatRequest , req: Request):
    def generate():
        for chunk in client.stream(
            prompt=request.prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            request_id=req.state.request_id
        ):
            yield chunk

    return StreamingResponse(
        generate(), 
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering if present
        }
    )