from pathlib import Path
from app.core.logging import get_logger
import yaml

PROMPT_BASE_PATH = Path("app/prompts")

logger = get_logger("prompt_loader")

class PromptLoader:
    def load(self, name: str, version: str) -> dict:
        try :   
            prompt_path = PROMPT_BASE_PATH / name / f"{version}.yaml"
            logger.info(
                "prompt_load_success",
                    extra={
                        "extra": {
                            "name": name,
                            "version": version,
                            "prompt_path": prompt_path,
                        }
                    }
                )
            with open(prompt_path, "r") as f:
                return yaml.safe_load(f)
            
        except Exception as e:
            logger.error(
                "prompt_load_failed",
                extra={
                    "extra": {
                        "name": name,
                        "version": version,
                        "error": str(e)
                    }
                }
            )
            raise

    def render(self, prompt: dict, variables: dict) -> str:
        try:
            user_prompt = prompt["user"]
            for key, value in variables.items():
                user_prompt = user_prompt.replace(f"{{{{{key}}}}}", value)

            logger.info(
                "prompt_render_success",
                extra={
                    "extra": {
                        "prompt": user_prompt,
                        "variables": variables
                    }
                }
            )
            return f"{prompt['system']}\n\n{user_prompt}"

        except Exception as e:
            logger.error(
                "prompt_render_failed",
                extra={
                    "extra": {
                        "prompt": prompt,
                        "variables": variables,
                        "error": str(e)
                    }
                }
            )
            raise

