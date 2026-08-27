"""
Imports every model so `Base.metadata` is complete wherever this module
is imported - needed for Alembic autogenerate and safe at app startup.
"""
from app.models.user import User  # noqa: F401
from app.models.business import Business  # noqa: F401
from app.models.business_profile import BusinessProfile  # noqa: F401
from app.models.goal import BusinessGoal  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.task import Task  # noqa: F401
from app.models.revenue_entry import RevenueEntry  # noqa: F401
from app.models.health_score import HealthScore  # noqa: F401
from app.models.business_plan import BusinessPlan  # noqa: F401
from app.models.ai_conversation import AIConversation  # noqa: F401
from app.models.ai_insight import AIInsight  # noqa: F401
from app.models.memory_record import MemoryRecord  # noqa: F401
from app.models.trade import Trade  # noqa: F401
from app.models.website_brief import WebsiteBrief  # noqa: F401
from app.models.stripe_connection import StripeConnection  # noqa: F401
from app.models.password_reset_token import PasswordResetToken  # noqa: F401
from app.models.google_calendar_connection import GoogleCalendarConnection  # noqa: F401
from app.models.opportunity_finding import OpportunityFinding  # noqa: F401