from langfuse import Langfuse
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("langfuse")
try:
    langfuse_client = Langfuse(
        secret_key=settings.langfuse_secret_key,
        public_key=settings.langfuse_public_key,
        host=settings.langfuse_host,
    )
    logger.info("Langfuse client initialized")
except Exception as e:
    logger.error("Failed to initialize Langfuse client", extra={"extra": {"error": str(e)}})
    raise e

