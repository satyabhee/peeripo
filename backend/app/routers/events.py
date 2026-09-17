from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/events", tags=["events"])


@router.post("")
def create_event(body: schemas.EventIn, admin_id: str, db: Session = Depends(get_db)):
    event = models.Event(
        name=body.name,
        event_type=body.event_type,
        notes=body.notes,
        created_by=admin_id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.post("/scores")
def add_event_score(body: schemas.EventScoreIn, db: Session = Depends(get_db)):
    score = models.EventScore(
        event_id=body.event_id, user_id=body.user_id, points=body.points
    )
    db.add(score)
    db.commit()
    db.refresh(score)
    return score
