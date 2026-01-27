from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str
    default_model: str

    # Prompt Ops
    summarizer_prompt_version: str = "v1"

    class Config:
        env_file = ".env"

settings = Settings()
