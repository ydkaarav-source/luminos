from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.dependencies.auth_dependencies import require_active_business
from app.dependencies.db_dependencies import get_db
from app.models.business import Business
from app.models.project import Project
from app.schemas.common import Envelope, ResponseMeta
from app.schemas.project import ProjectCreateRequest, ProjectOut, ProjectUpdateRequest

router = APIRouter(prefix="/projects", tags=["projects"])


def _envelope(data):
    return Envelope(data=data, meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))


def _get_owned(db: Session, project_id: UUID, business_id: UUID) -> Project:
    project = db.get(Project, project_id)
    if not project or project.business_id != business_id:
        raise NotFoundError("Project not found.")
    return project


@router.get("", response_model=Envelope[list[ProjectOut]])
def list_projects(business: Business = Depends(require_active_business), db: Session = Depends(get_db)):
    projects = db.query(Project).filter(Project.business_id == business.id).all()
    return _envelope([ProjectOut.model_validate(p) for p in projects])


@router.post("", response_model=Envelope[ProjectOut])
def create_project(
    payload: ProjectCreateRequest,
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    project = Project(business_id=business.id, **payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return _envelope(ProjectOut.model_validate(project))


@router.patch("/{project_id}", response_model=Envelope[ProjectOut])
def update_project(
    project_id: UUID,
    payload: ProjectUpdateRequest,
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    project = _get_owned(db, project_id, business.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.add(project)
    db.commit()
    db.refresh(project)
    return _envelope(ProjectOut.model_validate(project))


@router.delete("/{project_id}")
def delete_project(
    project_id: UUID,
    business: Business = Depends(require_active_business),
    db: Session = Depends(get_db),
):
    project = _get_owned(db, project_id, business.id)
    db.delete(project)
    db.commit()
    return _envelope({"deleted": True})
