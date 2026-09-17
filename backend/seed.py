"""Fill in the lists below with your real friend group / places, then run:

    python backend/seed.py

Safe to re-run — it upserts by name instead of duplicating rows. Prints each
user's generated id at the end; you'll need those for .env (LIFE360 mapping
happens separately, see worker/list_life360_members.py) and the frontend's
NEXT_PUBLIC_ADMIN_ID.
"""

from app.database import Base, SessionLocal, engine
from app.models import OptIn, OptInCategory, Place, User

# --- EDIT ME -----------------------------------------------------------

FRIENDS = [
    # name, is_admin, life360_member_id (fill in later via list_life360_members.py)
    {"name": "Satya", "is_admin": True, "life360_member_id": None},
    {"name": "Murari", "is_admin": False, "life360_member_id": None},
    {"name": "Vishakh", "is_admin": False, "life360_member_id": None},
]

PLACES = [
    # name, lat, lon, radius in meters
    {"name": "Gym", "lat": 0.0, "lon": 0.0, "radius_m": 100},
    {"name": "Library", "lat": 0.0, "lon": 0.0, "radius_m": 100},
]

# Categories every user starts with, all disabled until they opt in themselves
# via the settings page.
DEFAULT_OPT_IN_CATEGORIES = list(OptInCategory)

# -------------------------------------------------------------------------


def upsert_user(db, friend: dict) -> User:
    user = db.query(User).filter(User.name == friend["name"]).first()
    if user is None:
        user = User(
            name=friend["name"],
            is_admin=friend["is_admin"],
            life360_member_id=friend["life360_member_id"],
        )
        db.add(user)
        db.flush()
        print(f"  created user {friend['name']!r} -> {user.id}")
    else:
        user.is_admin = friend["is_admin"]
        if friend["life360_member_id"]:
            user.life360_member_id = friend["life360_member_id"]
        print(f"  existing user {friend['name']!r} -> {user.id}")
    return user


def ensure_opt_ins(db, user: User):
    existing = {o.category for o in db.query(OptIn).filter(OptIn.user_id == user.id)}
    for category in DEFAULT_OPT_IN_CATEGORIES:
        if category not in existing:
            db.add(OptIn(user_id=user.id, category=category, enabled=False))


def upsert_place(db, place: dict) -> Place:
    existing = db.query(Place).filter(Place.name == place["name"]).first()
    if existing is None:
        existing = Place(**place)
        db.add(existing)
        db.flush()
        print(f"  created place {place['name']!r} -> {existing.id}")
    else:
        existing.lat = place["lat"]
        existing.lon = place["lon"]
        existing.radius_m = place["radius_m"]
        print(f"  existing place {place['name']!r} -> {existing.id}")
    return existing


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("Users:")
        users = [upsert_user(db, f) for f in FRIENDS]
        for user in users:
            ensure_opt_ins(db, user)

        print("Places:")
        for place in PLACES:
            upsert_place(db, place)

        db.commit()

        print("\nDone. All opt-ins default to disabled — each friend needs to")
        print("enable their own categories from the settings page.")
        admin = next((u for u in users if u.is_admin), None)
        if admin:
            print(f"\nAdmin user id (put this in frontend NEXT_PUBLIC_ADMIN_ID): {admin.id}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
