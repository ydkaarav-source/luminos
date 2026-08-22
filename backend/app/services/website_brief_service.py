from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.ai_conversation import ConversationContext
from app.models.business import Business
from app.models.business_plan import BusinessPlan
from app.models.memory_record import MemorySource, MemoryType
from app.models.website_brief import WebsiteBrief
from app.repositories.business_profile_repository import BusinessProfileRepository
from app.services.ai.ai_orchestrator import AIOrchestrator
from app.services.ai.prompt_templates import website_brief as prompt_template
from app.services.website_scraper_service import WebsiteScraperService


class WebsiteBriefService:
    def __init__(self, db: Session):
        self.db = db
        self.ai = AIOrchestrator(db)
        self.profile_repo = BusinessProfileRepository(db)
        self.scraper = WebsiteScraperService()

    async def generate_brief(self, business: Business, user_id: UUID) -> WebsiteBrief:
        memory_lines = self.ai.get_memory_context(
            business.id, memory_types=[MemoryType.DECISION, MemoryType.PREFERENCE, MemoryType.FACT]
        )

        profile = self.profile_repo.get_by_business_id(business.id)
        business_context = {
            "industry": profile.industry if profile else None,
            "description": profile.description if profile else None,
            "products_services": profile.products_services if profile else None,
            "target_customers": profile.target_customers if profile else None,
            "company_goals": profile.company_goals if profile else None,
        }

        latest_plan = (
            self.db.query(BusinessPlan)
            .filter(BusinessPlan.business_id == business.id)
            .order_by(BusinessPlan.created_at.desc())
            .first()
        )
        plan_context = (
            {"overview": latest_plan.overview, "roadmap": latest_plan.roadmap} if latest_plan else None
        )

        system_prompt, user_prompt = prompt_template.build_prompt(business_context, plan_context, memory_lines)

        raw = await self.ai.run(
            business_id=business.id,
            user_id=user_id,
            context_type=ConversationContext.WEBSITE_BRIEF,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_mode=True,
        )
        parsed = self.ai.run_json(raw)

        brief = WebsiteBrief(
            business_id=business.id,
            title=parsed["title"],
            target_pages=parsed["target_pages"],
            copy_direction=parsed["copy_direction"],
            design_direction=parsed["design_direction"],
        )
        self.db.add(brief)
        self.db.commit()
        self.db.refresh(brief)

        # A generated website brief is a real strategic artifact other AI
        # features (CEO Briefing, the Assistant) should be aware exists.
        self.ai.remember(
            business.id,
            f"Generated website brief '{brief.title}'",
            MemoryType.DECISION,
            MemorySource.WEBSITE_BRIEF,
        )

        return brief

    def get_latest(self, business_id: UUID) -> WebsiteBrief | None:
        return (
            self.db.query(WebsiteBrief)
            .filter(WebsiteBrief.business_id == business_id)
            .order_by(WebsiteBrief.created_at.desc())
            .first()
        )

    async def scrape_site(self, business: Business, url: str) -> tuple[WebsiteBrief, str]:
        """
        Fetches the founder's real, live site and records what was
        actually found. Raises WebsiteUnreachableError (via the
        scraper) on any failure - nothing is written to site_url or
        memory_records unless the fetch genuinely succeeded.
        """
        brief = self.get_latest(business.id)
        if not brief:
            raise NotFoundError("Generate a website brief before checking your site.")

        content = await self.scraper.scrape(url)

        brief.site_url = url
        self.db.add(brief)
        self.db.commit()
        self.db.refresh(brief)

        # Real content pulled from the founder's own live site - a
        # distinct kind of fact from the AI-generated brief above, so it
        # gets its own MemorySource rather than being conflated with it.
        self.ai.remember(
            business.id,
            f"Real content found on the founder's live site ({url}): {content}",
            MemoryType.FACT,
            MemorySource.SCRAPED_SITE_CONTENT,
        )

        return brief, content
