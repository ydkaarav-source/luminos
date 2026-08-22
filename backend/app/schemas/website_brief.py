from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel


class WebsiteBriefGenerateRequest(BaseModel):
    pass


class WebsiteScrapeRequest(BaseModel):
    url: AnyHttpUrl


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


class WebsiteScrapeResponse(BaseModel):
    brief: WebsiteBriefOut
    content_preview: str
