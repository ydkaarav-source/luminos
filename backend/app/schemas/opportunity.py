from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.opportunity_finding import OpportunityFindingSeverity, OpportunityFindingType


class OpportunityFindingOut(BaseModel):
    id: UUID
    finding_type: OpportunityFindingType
    severity: OpportunityFindingSeverity
    title: str
    details: dict
    detected_at: datetime

    model_config = {"from_attributes": True}
