from uuid import UUID

from sqlalchemy.orm import Session

from app.models.ai_conversation import ConversationContext
from app.models.business import Business
from app.models.business_plan import BusinessPlan
from app.models.memory_record import MemorySource, MemoryType
from app.services.ai.ai_orchestrator import AIOrchestrator
from app.services.ai.prompt_templates import business_builder as prompt_template


class BusinessBuilderService:
    def __init__(self, db: Session):
        self.db = db
        self.ai = AIOrchestrator(db)

    async def generate_plan(self, business: Business, idea_description: str, user_id: UUID) -> BusinessPlan:
        memory_lines = self.ai.get_memory_context(
            business.id, memory_types=[MemoryType.DECISION, MemoryType.PREFERENCE, MemoryType.FACT]
        )

        context = {
            "stage": business.stage.value,
            "business_type": business.business_type.value,
            "primary_goal": business.primary_goal.value,
            "available_time_per_week": business.available_time_per_week,
            "budget_range": business.budget_range.value if business.budget_range else None,
        }

        system_prompt, user_prompt = prompt_template.build_prompt(idea_description, context, memory_lines)

        raw = await self.ai.run(
            business_id=business.id,
            user_id=user_id,
            context_type=ConversationContext.BUSINESS_BUILDER,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_mode=True,
        )
        parsed = self.ai.run_json(raw)

        plan = BusinessPlan(
            business_id=business.id,
            title=parsed["title"],
            overview=parsed["overview"],
            roadmap=parsed["roadmap"],
            action_plan=parsed["action_plan"],
        )
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)

        # This generated plan reflects a real strategic decision - worth remembering.
        self.ai.remember(
            business.id,
            f"Generated business plan '{plan.title}' for idea: {idea_description}",
            MemoryType.DECISION,
            MemorySource.BUSINESS_BUILDER,
        )

        return plan

    def list_plans(self, business_id: UUID) -> list[BusinessPlan]:
        return (
            self.db.query(BusinessPlan)
            .filter(BusinessPlan.business_id == business_id)
            .order_by(BusinessPlan.created_at.desc())
            .all()
        )

    def get_plan(self, plan_id: UUID) -> BusinessPlan | None:
        return self.db.get(BusinessPlan, plan_id)
