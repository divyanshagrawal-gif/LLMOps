from google import genai
from app.core.config import settings
from app.core.logging import get_logger
import time


logger = get_logger("gemini")

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
        request_id=None
    ):
        try:
            model_name = model or settings.default_model
            start = time.time()

            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens
                }
            )

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
        request_id=None
    ):
        try:
            model_name = model or settings.default_model
            start = time.time()


            response = self.client.models.generate_content_stream(
                model=model_name,
                contents=prompt,
                config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens
                }
            )

            latency = time.time() - start

            logger.info(
                "llm_stream_call_success",
                    extra={
                        "extra": {
                            "request_id": request_id,
                            "model": model_name,
                            "latency": latency,
                            "prompt_length": len(prompt),
                        }
                    }
                )

            for chunk in response:
                if chunk.text:
                    yield chunk.text

            yield f"\n\n[MODEL={model_name} | LATENCY={latency}s]"

        except Exception as e:
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