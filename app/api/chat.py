from fastapi import APIRouter, Request
from app.schemas.chat import ChatRequest, ChatResponse
from fastapi.responses import StreamingResponse
from app.services import prompt_loader
# from app.services.gemini_client import GeminiClient
from app.services.prompt_loader import PromptLoader
from app.services.llm_service import generate_with_cache
from app.core.config import settings
from app.services.prompt_router import PromptRouter

router = APIRouter()
# client = GeminiClient()
prompt_loader = PromptLoader()
prompt_router = PromptRouter(variants=["v1", "v2"])

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, req: Request):
    result, cache_hit = generate_with_cache(
        prompt=request.prompt,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        request_id=req.state.request_id,
        stream = False,
        prompt_version="N/A"
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
            stream = True,
            prompt_version="N/A"
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
        version=settings.summarizer_prompt_version
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
        stream=False,
        prompt_version=settings.summarizer_prompt_version
    )

    return {
        "summary": result["text"],
        "model": result["model"],
        "cache_hit": cache_hit,
        "prompt_version": settings.summarizer_prompt_version
    }


@router.post("/summarize/ab")
def summarize_ab(request: ChatRequest, req: Request):
    version = prompt_router.choose()

    prompt_def = prompt_loader.load("summarizer", version)
    final_prompt = prompt_loader.render(
        prompt_def,
        {"text": request.prompt}
    )

    result, cache_hit = generate_with_cache(
        prompt=final_prompt,
        temperature=0.3,
        max_tokens=request.max_tokens,
        request_id=req.state.request_id,
        stream=False,
        prompt_version=version
    )

    return {
        "summary": result["text"],
        "summarizer_prompt_version": version,
        "cache_hit": cache_hit
    }