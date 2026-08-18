from uuid import UUID

from pydantic import BaseModel


class BusinessProfileCreateRequest(BaseModel):
    industry: str | None = None
    description: str | None = None
    products_services: str | None = None
    target_customers: str | None = None
    company_goals: str | None = None


class BusinessProfileOut(BaseModel):
    id: UUID
    business_id: UUID
    industry: str | None
    description: str | None
    products_services: str | None
    target_customers: str | None
    company_goals: str | None

    model_config = {"from_attributes": True}
