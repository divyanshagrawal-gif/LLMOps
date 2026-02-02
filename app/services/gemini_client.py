from google import genai
from app.core.config import settings
from app.core.logging import get_logger
import time

logger = get_logger("gemini")


def _usage_from_response(response) -> dict | None:
    """Extract token usage from Gemini response for Langfuse (OpenAI-style: promptTokens, completionTokens, totalTokens)."""
    # print("response", response)
    usage_meta = getattr(response, "usage_metadata", None) 
    # print("usage_meta", usage_meta)
    if usage_meta is None:
        return None
    prompt_tokens = getattr(usage_meta, "prompt_token_count", None) or getattr(usage_meta, "input_token_count", None)
    completion_tokens = getattr(usage_meta, "candidates_token_count", None) or getattr(usage_meta, "output_token_count", None)
    total_tokens = getattr(usage_meta, "total_token_count", None)
    thought_tokens = getattr(usage_meta, "thoughts_token_count", None)
    if prompt_tokens is None and completion_tokens is None and total_tokens is None:
        return None
    if total_tokens is None and (prompt_tokens is not None or completion_tokens is not None):
        total_tokens = (prompt_tokens or 0) + (completion_tokens or 0)
    # Langfuse expects OpenAI-style keys for token display
    return {
        "promptTokens": prompt_tokens or 0,
        "completionTokens": completion_tokens or 0,
        "totalTokens": total_tokens or 0,
    }


class GeminiClient:
    def __init__(self):
        client = genai.Client(api_key=settings.gemini_api_key)
        self.client = client

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        request_id=None,
        trace=None,
    ):
        model_name = model or settings.default_model
        start = time.time()
        try:
            generation = None
            if trace:
                generation = trace.generation(
                    name="gemini-generate",
                    model=model_name,
                    input={"prompt": prompt, "model": model_name, "temperature": temperature, "max_tokens": max_tokens},
                    metadata={"request_id": request_id} if request_id else None,
                )
            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens
                }
            )
            if generation:
                usage = _usage_from_response(response)
                generation.end(output=response.text or "", usage=usage)
            latency = time.time() - start
            logger.info(
                "llm_chat_call_success",
                extra={
                    "extra": {
                        "request_id": request_id,
                        "model": model_name,
                        "latency": latency,
                        "prompt_length": len(prompt),
                        "response_length": len(response.text or "")
                    }
                }
            )
            return {
                "text": response.text,
                "model": model_name,
                "latency": latency
            }
        except Exception as e:
            if generation:
                try:
                    generation.end(output=None, level="ERROR", status_message=str(e))
                except Exception:
                    pass
            logger.error(
                "llm_chat_call_failed",
                extra={
                    "extra": {
                        "request_id": request_id,
                        "model": model_name,
                        "error": str(e)
                    }
                }
            )
            raise
        
    def stream(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        request_id=None,
        trace=None,
    ):
        model_name = model or settings.default_model
        start = time.time()
        generation = None
        try:
            if trace:
                generation = trace.generation(
                    name="gemini-stream",
                    model=model_name,
                    input={"prompt": prompt, "model": model_name, "temperature": temperature, "max_tokens": max_tokens},
                    metadata={"request_id": request_id} if request_id else None,
                )
            response = self.client.models.generate_content_stream(
                model=model_name,
                contents=prompt,
                config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens
                }
            )
            full_text = ""
            last_chunk = None
            for chunk in response:
                last_chunk = chunk
                if chunk.text:
                    full_text += chunk.text
                    yield chunk.text
            yield f"\n\n[MODEL={model_name} | LATENCY={time.time() - start:.2f}s]"
            if generation:
                usage = _usage_from_response(last_chunk) if last_chunk else None
                generation.end(output=full_text, usage=usage)
            logger.info(
                "llm_stream_call_success",
                extra={
                    "extra": {
                        "request_id": request_id,
                        "model": model_name,
                        "latency": time.time() - start,
                        "prompt_length": len(prompt),
                    }
                }
            )
        except Exception as e:
            if generation:
                try:
                    generation.end(output=None, level="ERROR", status_message=str(e))
                except Exception:
                    pass
            logger.error(
                "llm_stream_call_failed",
                extra={
                    "extra": {
                        "request_id": request_id,
                        "model": model_name,
                        "error": str(e)
                    }
                }
            )
            raise