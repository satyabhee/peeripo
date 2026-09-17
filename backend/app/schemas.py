from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .models import AuraScoreStatus, OptInCategory


class UserOut(BaseModel):
    id: str
    name: str
    is_admin: bool

    class Config:
        from_attributes = True


class OptInIn(BaseModel):
    category: OptInCategory
    enabled: bool


class OptInOut(OptInIn):
    id: str
    user_id: str

    class Config:
        from_attributes = True


class EventIn(BaseModel):
    name: str
    event_type: str
    notes: Optional[str] = None


class EventScoreIn(BaseModel):
    event_id: str
    user_id: str
    points: float


class AuraScoreOut(BaseModel):
    id: str
    user_id: str
    points: float
    note: Optional[str]
    status: AuraScoreStatus
    created_at: datetime

    class Config:
        from_attributes = True


class AuraScoreReview(BaseModel):
    status: AuraScoreStatus
    points: Optional[float] = None  # allow admin to edit before approving


class StockPriceOut(BaseModel):
    user_id: str
    price: float
    fundamentals_score: float
    recorded_at: datetime

    class Config:
        from_attributes = True
