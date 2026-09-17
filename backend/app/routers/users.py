from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[schemas.UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


@router.get("/{user_id}/opt-ins", response_model=list[schemas.OptInOut])
def get_opt_ins(user_id: str, db: Session = Depends(get_db)):
    return db.query(models.OptIn).filter(models.OptIn.user_id == user_id).all()


@router.put("/{user_id}/opt-ins", response_model=schemas.OptInOut)
def set_opt_in(user_id: str, body: schemas.OptInIn, db: Session = Depends(get_db)):
    opt_in = (
        db.query(models.OptIn)
        .filter(models.OptIn.user_id == user_id, models.OptIn.category == body.category)
        .first()
    )
    if opt_in is None:
        opt_in = models.OptIn(user_id=user_id, category=body.category, enabled=body.enabled)
        db.add(opt_in)
    else:
        opt_in.enabled = body.enabled
    db.commit()
    db.refresh(opt_in)
    return opt_in
