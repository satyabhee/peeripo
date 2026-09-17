"""Pulls listening stats via Spotify's official Web API (OAuth per user).

Each friend authorizes the app through Spotify's normal OAuth consent screen;
we only ever request read-only scopes (user-read-recently-played, user-top-read).
"""

from datetime import datetime

import spotipy

from . import config
from .db import SessionLocal, models


def client_for(refresh_token: str) -> spotipy.Spotify:
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        client_id=config.SPOTIFY_CLIENT_ID,
        client_secret=config.SPOTIFY_CLIENT_SECRET,
        redirect_uri="http://localhost:8000/spotify/callback",
        scope="user-read-recently-played user-top-read",
    )
    token_info = auth_manager.refresh_access_token(refresh_token)
    return spotipy.Spotify(auth=token_info["access_token"])


def poll_once():
    db = SessionLocal()
    try:
        accounts = db.query(models.SpotifyAccount).all()
        for account in accounts:
            refresh_token = config.decrypt(account.encrypted_refresh_token)
            sp = client_for(refresh_token)

            recent = sp.current_user_recently_played(limit=50)
            track_ids = [item["track"]["id"] for item in recent["items"]]
            minutes_listened = sum(item["track"]["duration_ms"] for item in recent["items"]) / 60000

            avg_valence, avg_energy = None, None
            if track_ids:
                features = sp.audio_features(track_ids)
                valid = [f for f in features if f]
                if valid:
                    avg_valence = sum(f["valence"] for f in valid) / len(valid)
                    avg_energy = sum(f["energy"] for f in valid) / len(valid)

            db.add(
                models.SpotifyStat(
                    user_id=account.user_id,
                    date=datetime.utcnow(),
                    minutes_listened=minutes_listened,
                    avg_valence=avg_valence,
                    avg_energy=avg_energy,
                )
            )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    poll_once()
