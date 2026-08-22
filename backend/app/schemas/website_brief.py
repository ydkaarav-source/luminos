from uuid import UUID

from pydantic import BaseModel


class WebsiteBriefGenerateRequest(BaseModel):
    pass


class TargetPage(BaseModel):
    name: str
    purpose: str


class WebsiteBriefOut(BaseModel):
    id: UUID
    title: str
    target_pages: list[TargetPage]
    copy_direction: str
    design_direction: str
    site_url: str | None

    model_config = {"from_attributes": True}
