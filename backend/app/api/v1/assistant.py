from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.auth_dependencies import get_current_user, require_active_business
from app.dependencies.db_dependencies import get_db
from app.models.business import Business
from app.models.user import User
from app.schemas.ai import AssistantMessageOut, AssistantMessageRequest
from app.schemas.common import Envelope, ResponseMeta
from app.services.assistant_service import AssistantService

router = APIRouter(prefix="/assistant", tags=["assistant"])


def _envelope(data):
    return Envelope(data=data, meta=ResponseMeta(generated_at=datetime.now(timezone.utc)))


@router.get("/conversations", response_model=Envelope[list[AssistantMessageOut]])
def conversations(business: Business = Depends(require_active_business), db: Session = Depends(get_db)):
    turns = AssistantService(db).get_conversation(business.id)
    return _envelope([AssistantMessageOut.model_validate(t) for t in turns])


@router.post("/message", response_model=Envelope[AssistantMessageOut])
async def send_message(
    payload: AssistantMessageRequest,
    business: Business = Depends(require_active_business),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reply = await AssistantService(db).send_message(business, current_user.id, payload.content)
    return _envelope(AssistantMessageOut.model_validate(reply))
