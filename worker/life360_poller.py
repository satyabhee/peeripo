"""Pulls circle member locations using YOUR OWN Life360 login.

Uses the unofficial `life360` PyPI client rather than each friend's credentials --
since you're already a member of the shared Circle, authenticating as yourself is
enough to see every opted-in member's location. This talks to an undocumented,
unofficial API: it can break on Life360 changes and technically isn't sanctioned
by their ToS, which is a known tradeoff for this project (see project notes).
"""

from datetime import datetime

from life360 import Life360

from . import config
from .db import SessionLocal, models
from .geofence import match_place

_client = None


def get_client() -> Life360:
    global _client
    if _client is None:
        _client = Life360(
            username=config.LIFE360_USERNAME,
            password=config.LIFE360_PASSWORD,
        )
        _client.authenticate()
    return _client


def poll_once():
    db = SessionLocal()
    try:
        client = get_client()
        circles = client.get_circles()
        circle = next((c for c in circles if c["name"] == config.LIFE360_CIRCLE_NAME), None)
        if circle is None:
            raise RuntimeError(f"Circle '{config.LIFE360_CIRCLE_NAME}' not found")

        members = client.get_circle_members(circle["id"])
        places = db.query(models.Place).all()
        opted_in_ids = {
            o.user_id
            for o in db.query(models.OptIn).filter(
                models.OptIn.category == models.OptInCategory.location,
                models.OptIn.enabled == True,  # noqa: E712
            )
        }

        for member in members:
            user = (
                db.query(models.User)
                .filter(models.User.life360_member_id == member["id"])
                .first()
            )
            if user is None or user.id not in opted_in_ids:
                continue

            loc = member.get("location")
            if not loc:
                continue

            lat, lon = float(loc["latitude"]), float(loc["longitude"])
            place_id = match_place(lat, lon, places)

            db.add(
                models.Life360Ping(
                    user_id=user.id,
                    lat=lat,
                    lon=lon,
                    accuracy_m=float(loc.get("accuracy", 0)),
                    place_id=place_id,
                    recorded_at=datetime.utcnow(),
                )
            )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    poll_once()
