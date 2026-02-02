# this is the main orchestration file between the cache and the gemini client

from app.services.cache import CacheService
from app.services.gemini_client import GeminiClient
from app.core.logging import get_logger
from app.core.config import settings
logger = get_logger("llm_service")

cache = CacheService()
client = GeminiClient()

def _simulate_streaming(text, chunk_size=50):
    """Simulate streaming by chunking cached text"""
    for i in range(0, len(text), chunk_size):
        yield text[i:i + chunk_size]

def generate_with_cache(prompt, temperature, max_tokens, request_id, stream, prompt_version=None, trace=None):
    model = settings.default_model
    cached = cache.get(prompt, model, temperature)
    if cached:
        logger.info(
            "cache_hit",
            extra={
                "extra": {
                    "request_id": request_id,
                    "prompt": prompt,
                    "model": model,
                    "temperature": temperature,
                    "prompt_version": prompt_version
                }
            }
        )

        if stream:
            # For streaming cache hits, simulate streaming from cached text
            def cached_stream():
                cached_text = cached.get("text", "")
                for chunk in _simulate_streaming(cached_text):
                    yield chunk
                # Include metadata if present
                if "\n\n[MODEL=" in cached_text:
                    # Metadata already in text
                    pass
                else:
                    yield f"\n\n[MODEL={cached.get('model', model)} | CACHED]"
            return cached_stream(), True
        else:
            return cached, True

    else:
        logger.info(
            "cache_miss",
            extra={
                "extra": {
                    "request_id": request_id,
                    "prompt": prompt,
                    "model": model,
                    "temperature": temperature,
                    "prompt_version": prompt_version
                }
            }
        )

    if stream:
        # For streaming cache misses, collect chunks and cache after streaming
        def streaming_with_cache():
            chunks = []
            full_text = ""
            
            for chunk in client.stream(
                prompt=prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                request_id=request_id,
                trace=trace,
            ):
                chunks.append(chunk)
                full_text += chunk
                yield chunk
            
            # Cache the full response after streaming completes
            result = {
                "text": full_text,
                "model": model,
                "latency": 0,  # Latency already logged in client
                "prompt_version": prompt_version
            }
            cache.set(prompt, model, temperature, result)
            
        return streaming_with_cache(), False
    else:
        result = client.generate(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            request_id=request_id,
            trace=trace,
        )
        cache.set(prompt, model, temperature, result)
        return result, False

