"""Computes each friend's daily 'fundamentals' score and turns it into a stock
price using geometric Brownian motion, with the fundamentals score driving the
drift term. Small random noise (volatility) keeps it feeling like a real market
even on days where nothing changed.
"""

import math
import random
from collections import defaultdict
from datetime import datetime, timedelta

from .db import SessionLocal, models

VOLATILITY = 0.02  # daily sigma
DT = 1.0  # one day per tick

WEIGHTS = {
    "gym_hours": 3.0,
    "library_hours": 2.0,
    "grade_avg": 0.5,  # applied to (grade_avg - 85), so above/below a baseline moves price
    "event_points": 1.0,
    "aura_points": 1.0,
    "spotify_valence": 5.0,
}


def compute_fundamentals(db, user_id: str, since: datetime) -> float:
    pings = (
        db.query(models.Life360Ping)
        .filter(models.Life360Ping.user_id == user_id, models.Life360Ping.recorded_at >= since)
        .all()
    )
    place_names = {p.id: p.name for p in db.query(models.Place).all()}

    hours_per_place = defaultdict(float)
    # each ping ~ one polling interval; caller's poller cadence determines the unit here
    ping_interval_hours = 0.25
    for ping in pings:
        if ping.place_id:
            hours_per_place[place_names.get(ping.place_id, "")] += ping_interval_hours

    grades = (
        db.query(models.CanvasGrade)
        .filter(models.CanvasGrade.user_id == user_id, models.CanvasGrade.recorded_at >= since)
        .all()
    )
    grade_avg = sum(g.current_score for g in grades if g.current_score is not None) / len(grades) if grades else 85.0

    event_points = sum(
        s.points
        for s in db.query(models.EventScore).filter(models.EventScore.user_id == user_id)
        if s.id  # all-time; could filter by event.happened_at >= since if desired
    )

    aura_points = sum(
        a.points
        for a in db.query(models.AuraScore).filter(
            models.AuraScore.user_id == user_id,
            models.AuraScore.status == models.AuraScoreStatus.approved,
            models.AuraScore.created_at >= since,
        )
    )

    spotify_stats = (
        db.query(models.SpotifyStat)
        .filter(models.SpotifyStat.user_id == user_id, models.SpotifyStat.date >= since)
        .all()
    )
    avg_valence = (
        sum(s.avg_valence for s in spotify_stats if s.avg_valence is not None) / len(spotify_stats)
        if spotify_stats
        else 0.5
    )

    fundamentals = (
        WEIGHTS["gym_hours"] * hours_per_place.get("Gym", 0.0)
        + WEIGHTS["library_hours"] * hours_per_place.get("Library", 0.0)
        + WEIGHTS["grade_avg"] * (grade_avg - 85.0)
        + WEIGHTS["event_points"] * event_points
        + WEIGHTS["aura_points"] * aura_points
        + WEIGHTS["spotify_valence"] * (avg_valence - 0.5)
    )
    return fundamentals


def next_price(previous_price: float, fundamentals_score: float) -> float:
    """Geometric Brownian motion: dS = mu*S*dt + sigma*S*dW.

    `fundamentals_score` is mapped to the drift (mu) -- a good day (lots of gym/
    library time, good grades, positive aura) pushes drift positive.
    """
    mu = fundamentals_score * 0.01  # scale factor tuned to taste
    dW = random.gauss(0, math.sqrt(DT))
    return previous_price * math.exp((mu - 0.5 * VOLATILITY**2) * DT + VOLATILITY * dW)


def run_daily_tick():
    db = SessionLocal()
    try:
        since = datetime.utcnow() - timedelta(days=1)
        users = db.query(models.User).all()
        for user in users:
            last_price_row = (
                db.query(models.StockPrice)
                .filter(models.StockPrice.user_id == user.id)
                .order_by(models.StockPrice.recorded_at.desc())
                .first()
            )
            previous_price = last_price_row.price if last_price_row else 100.0

            fundamentals = compute_fundamentals(db, user.id, since)
            price = next_price(previous_price, fundamentals)

            db.add(
                models.StockPrice(
                    user_id=user.id,
                    price=price,
                    fundamentals_score=fundamentals,
                    recorded_at=datetime.utcnow(),
                )
            )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run_daily_tick()
