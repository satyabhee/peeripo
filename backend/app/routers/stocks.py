from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("/{user_id}/history", response_model=list[schemas.StockPriceOut])
def stock_history(user_id: str, db: Session = Depends(get_db)):
    return (
        db.query(models.StockPrice)
        .filter(models.StockPrice.user_id == user_id)
        .order_by(models.StockPrice.recorded_at)
        .all()
    )


@router.get("/leaderboard", response_model=list[schemas.StockPriceOut])
def leaderboard(db: Session = Depends(get_db)):
    """Latest price per user, highest first. Only for users opted into stock_visible."""
    visible_user_ids = {
        o.user_id
        for o in db.query(models.OptIn).filter(
            models.OptIn.category == models.OptInCategory.stock_visible,
            models.OptIn.enabled == True,  # noqa: E712
        )
    }
    latest = {}
    for row in db.query(models.StockPrice).order_by(models.StockPrice.recorded_at):
        if row.user_id in visible_user_ids:
            latest[row.user_id] = row
    return sorted(latest.values(), key=lambda r: r.price, reverse=True)
