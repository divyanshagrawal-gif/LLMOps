import random

class PromptRouter:
    def __init__(self, variants: list[str]):
        self.variants = variants

    def choose(self) -> str:
        return random.choice(self.variants)
