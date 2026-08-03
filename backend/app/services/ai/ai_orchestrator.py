"""
The single entry point every feature uses to talk to AI.

No feature service (business_builder_service, ceo_briefing_service,
health_score_service, assistant) ever imports a provider directly.
They all call `AIOrchestrator`, which:
  1. Resolves the configured provider (OpenAI today; swappable via
     `AI_PROVIDER` in settings).
  2. Delegates prompt construction to the caller (feature-specific
     prompt templates live in `prompt_templates/`).
  3. Logs the exchange to `ai_conversations` for traceability.
  4. Exposes a helper to persist new facts back to `memory_records`.
"""
import json
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models.ai_conversation import AIConversation, ConversationContext, ConversationRole
from app.models.memory_record import MemoryRecord, MemorySource, MemoryType
from app.repositories.memory_repository import MemoryRepository
from app.services.ai.openai_provider import OpenAIProvider
from app.services.ai.provider_interface import AIProviderInterface

logger = get_logger(__name__)


def _get_provider() -> AIProviderInterface:
    # This is the one branch point for adding a new provider later.
    if settings.AI_PROVIDER == "openai":
        return OpenAIProvider()
    raise ValueError(f"Unknown AI provider configured: {settings.AI_PROVIDER}")


class AIOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.provider = _get_provider()
        self.memory_repo = MemoryRepository(db)

    def get_memory_context(
        self, business_id: UUID, memory_types: list[MemoryType] | None = None
    ) -> list[str]:
        records = self.memory_repo.retrieve(business_id, memory_types=memory_types)
        return [r.content for r in records]

    async def run(
        self,
        *,
        business_id: UUID,
        user_id: UUID,
        context_type: ConversationContext,
        system_prompt: str,
        user_prompt: str,
        json_mode: bool = False,
    ) -> str:
        result = await self.provider.generate(system_prompt, user_prompt, json_mode=json_mode)

        self._log_conversation(business_id, user_id, context_type, ConversationRole.USER, user_prompt)
        self._log_conversation(business_id, user_id, context_type, ConversationRole.ASSISTANT, result)

        return result

    def run_json(self, raw: str) -> dict:
        """Best-effort JSON parse with a clear error if the model misbehaves."""
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.error("AI response was not valid JSON: %s", raw[:500])
            raise

    def remember(
        self,
        business_id: UUID,
        content: str,
        memory_type: MemoryType,
        source: MemorySource,
    ) -> MemoryRecord:
        record = MemoryRecord(
            business_id=business_id, content=content, memory_type=memory_type, source=source
        )
        return self.memory_repo.add(record)

    def _log_conversation(
        self,
        business_id: UUID,
        user_id: UUID,
        context_type: ConversationContext,
        role: ConversationRole,
        content: str,
    ) -> None:
        self.db.add(
            AIConversation(
                business_id=business_id,
                user_id=user_id,
                role=role,
                context_type=context_type,
                content=content,
            )
        )
        self.db.commit()
