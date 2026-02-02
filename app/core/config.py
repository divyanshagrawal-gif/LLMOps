from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str
    default_model: str
    langfuse_secret_key: str
    langfuse_public_key: str
    langfuse_host: str

    # Prompt Ops
    summarizer_prompt_version: str = "v1"

    class Config:
        env_file = ".env"

settings = Settings()
