from uuid import UUID

from sqlalchemy.orm import Session

from app.models.ai_conversation import AIConversation, ConversationContext, ConversationRole
from app.models.business import Business
from app.services.ai.ai_orchestrator import AIOrchestrator
from app.services.ai.prompt_templates import assistant as prompt_template


class AssistantService:
    def __init__(self, db: Session):
        self.db = db
        self.ai = AIOrchestrator(db)

    def get_conversation(self, business_id: UUID, limit: int = 50) -> list[AIConversation]:
        return (
            self.db.query(AIConversation)
            .filter(
                AIConversation.business_id == business_id,
                AIConversation.context_type == ConversationContext.ASSISTANT_CHAT,
            )
            .order_by(AIConversation.created_at.asc())
            .limit(limit)
            .all()
        )

    async def send_message(self, business: Business, user_id: UUID, content: str) -> AIConversation:
        memory_lines = self.ai.get_memory_context(business.id)

        recent = self.get_conversation(business.id, limit=10)
        recent_turns = [f"{c.role.value}: {c.content}" for c in recent]

        system_prompt, user_prompt = prompt_template.build_prompt(content, memory_lines, recent_turns)

        raw = await self.ai.run(
            business_id=business.id,
            user_id=user_id,
            context_type=ConversationContext.ASSISTANT_CHAT,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_mode=False,
        )

        # The orchestrator already logged the user_prompt + raw response as
        # USER/ASSISTANT turns via `run()`. Fetch the assistant turn back out
        # so the route can return a clean, typed object.
        latest_assistant_turn = (
            self.db.query(AIConversation)
            .filter(
                AIConversation.business_id == business.id,
                AIConversation.context_type == ConversationContext.ASSISTANT_CHAT,
                AIConversation.role == ConversationRole.ASSISTANT,
            )
            .order_by(AIConversation.created_at.desc())
            .first()
        )
        return latest_assistant_turn
