from uuid import UUID

from pydantic import BaseModel

from app.models.project import ProjectStatus


class ProjectCreateRequest(BaseModel):
    name: str
    description: str | None = None


class ProjectUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    status: ProjectStatus | None = None


class ProjectOut(BaseModel):
    id: UUID
    name: str
    description: str | None
    status: ProjectStatus

    model_config = {"from_attributes": True}
