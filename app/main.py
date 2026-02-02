from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
import uuid

app = FastAPI(title="LLMOps Gemini Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


@app.middleware("http")
async def add_request_id_and_langfuse_trace(request: Request, call_next):
    request.state.request_id = str(uuid.uuid4())
    request.state.langfuse_trace = None
    try:
        from app.core.langfuse import langfuse_client
        request.state.langfuse_trace = langfuse_client.trace(
            name="llm-request",
            metadata={"request_id": request.state.request_id},
        )
    except Exception:
        pass
    response = await call_next(request)
    try:
        from app.core.langfuse import langfuse_client
        langfuse_client.flush()
    except Exception:
        pass
    response.headers["X-Request-ID"] = request.state.request_id
    return response

@app.get("/health")
def health():
    return {"status": "ok"}
