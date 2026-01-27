from fastapi import APIRouter, Request
from app.schemas.chat import ChatRequest, ChatResponse
from fastapi.responses import StreamingResponse
from app.services import prompt_loader
# from app.services.gemini_client import GeminiClient
from app.services.prompt_loader import PromptLoader
from app.services.llm_service import generate_with_cache


router = APIRouter()
# client = GeminiClient()
prompt_loader = PromptLoader()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, req: Request):
    result, cache_hit = generate_with_cache(
        prompt=request.prompt,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        request_id=req.state.request_id,
        stream = False
    )

    return ChatResponse(
        response=result["text"],
        model=result["model"],
        latency=result["latency"],
        cache_hit=cache_hit
    )

@router.post("/chat/stream")
def chat_stream(request: ChatRequest , req: Request):
    def generate():
        generator, cache_hit = generate_with_cache(
            prompt=request.prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            request_id=req.state.request_id,
            stream = True
        )
        for chunk in generator:
            yield chunk

    return StreamingResponse(
        generate(), 
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering if present
        }
    )

@router.post("/summarize")
def summarize(request: ChatRequest, req: Request):
    prompt_def = prompt_loader.load(
        name="summarizer",
        version="v1"
    )

    final_prompt = prompt_loader.render(
        prompt_def,
        {"text": request.prompt}
    )

    result, cache_hit = generate_with_cache(
        prompt=final_prompt,
        temperature=0.3,
        max_tokens=request.max_tokens,
        request_id=req.state.request_id,
        stream=False
    )

    return {
        "summary": result["text"],
        "model": result["model"],
        "cache_hit": cache_hit
    }