"""Pulls grades via Canvas's official REST API.

Each friend opts in by generating their own personal access token in
Canvas > Account > Settings > "New Access Token", which they hand you directly --
no credential sharing or scraping involved. Tokens are stored encrypted and each
friend can revoke theirs from Canvas at any time, which immediately cuts off access.
"""

from datetime import datetime

import requests

from . import config
from .db import SessionLocal, models


def fetch_grades(base_url: str, token: str) -> list[dict]:
    resp = requests.get(
        f"{base_url}/api/v1/users/self/enrollments",
        headers={"Authorization": f"Bearer {token}"},
        params={"include[]": "current_grading_period_scores"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def poll_once():
    db = SessionLocal()
    try:
        accounts = db.query(models.CanvasAccount).all()
        for account in accounts:
            token = config.decrypt(account.encrypted_token)
            enrollments = fetch_grades(account.canvas_base_url, token)
            for enrollment in enrollments:
                grades = enrollment.get("grades", {})
                score = grades.get("current_score")
                course_name = enrollment.get("course", {}).get("name", "Unknown course")
                db.add(
                    models.CanvasGrade(
                        user_id=account.user_id,
                        course_name=course_name,
                        current_score=score,
                        recorded_at=datetime.utcnow(),
                    )
                )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    poll_once()
