import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .database import Base


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    life360_member_id = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    opt_ins = relationship("OptIn", back_populates="user", uselist=False)


class OptInCategory(str, enum.Enum):
    location = "location"
    canvas = "canvas"
    spotify = "spotify"
    aura = "aura"
    stock_visible = "stock_visible"


class OptIn(Base):
    __tablename__ = "opt_ins"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    category = Column(Enum(OptInCategory), nullable=False)
    enabled = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="opt_ins")


class Place(Base):
    __tablename__ = "places"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)  # e.g. "Gym", "Library"
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    radius_m = Column(Float, default=100.0)


class Life360Ping(Base):
    __tablename__ = "life360_pings"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    accuracy_m = Column(Float, nullable=True)
    place_id = Column(UUID(as_uuid=False), ForeignKey("places.id"), nullable=True)
    recorded_at = Column(DateTime, nullable=False)


class CanvasAccount(Base):
    __tablename__ = "canvas_accounts"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    canvas_base_url = Column(String, nullable=False)  # e.g. https://school.instructure.com
    encrypted_token = Column(Text, nullable=False)


class CanvasGrade(Base):
    __tablename__ = "canvas_grades"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    course_name = Column(String, nullable=False)
    current_score = Column(Float, nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow)


class SpotifyAccount(Base):
    __tablename__ = "spotify_accounts"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    encrypted_refresh_token = Column(Text, nullable=False)


class SpotifyStat(Base):
    __tablename__ = "spotify_stats"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    minutes_listened = Column(Float, default=0.0)
    avg_valence = Column(Float, nullable=True)  # spotify audio feature, 0-1 "positivity"
    avg_energy = Column(Float, nullable=True)


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)  # "Halloweekend", "Fantasy League Week 3"
    event_type = Column(String, nullable=False)
    happened_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)


class EventScore(Base):
    __tablename__ = "event_scores"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    event_id = Column(UUID(as_uuid=False), ForeignKey("events.id"), nullable=False)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    points = Column(Float, nullable=False)


class AuraScoreStatus(str, enum.Enum):
    suggested = "suggested"
    approved = "approved"
    rejected = "rejected"


class AuraScore(Base):
    __tablename__ = "aura_scores"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    points = Column(Float, nullable=False)
    note = Column(Text, nullable=True)
    source_screenshot = Column(String, nullable=True)
    status = Column(Enum(AuraScoreStatus), default=AuraScoreStatus.suggested)
    entered_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    price = Column(Float, nullable=False)
    fundamentals_score = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)
