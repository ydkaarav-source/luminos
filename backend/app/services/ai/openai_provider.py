"""
Concrete OpenAI implementation of AIProviderInterface.

This is the ONLY file in the app that imports the `openai` SDK. If
LuminOS adds a second provider (or moves off OpenAI entirely), this
file is what gets replaced or added alongside - everything else is
untouched.
"""
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.exceptions import AIProviderError
from app.core.logging import get_logger
from app.services.ai.provider_interface import AIProviderInterface

logger = get_logger(__name__)


class OpenAIProvider(AIProviderInterface):
    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        json_mode: bool = False,
        temperature: float = 0.4,
    ) -> str:
        try:
            response = await self._client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                temperature=temperature,
                response_format={"type": "json_object"} if json_mode else {"type": "text"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            content = response.choices[0].message.content
            if not content:
                raise AIProviderError("The AI provider returned an empty response.")
            return content
        except Exception as exc:  # noqa: BLE001
            logger.error("OpenAI request failed: %s", exc)
            raise AIProviderError("The AI assistant is temporarily unavailable.") from exc
