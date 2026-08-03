"""
Abstract interface every AI provider must implement.

Nothing outside this `ai/` package should ever import an SDK (openai,
anthropic, etc.) directly. Feature services call `AIOrchestrator`,
which calls whichever provider is configured. Adding a new provider is
writing one new class here and flipping `AI_PROVIDER` in settings -
no changes to prompts, routes, or business logic.
"""
from abc import ABC, abstractmethod


class AIProviderInterface(ABC):
    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        json_mode: bool = False,
        temperature: float = 0.4,
    ) -> str:
        """Return the model's raw text (or JSON string) response."""
        raise NotImplementedError
