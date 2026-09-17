"""Automates the *capture* of aura data, not the *access*.

You screenshot your own Instagram group chat (e.g. via a scheduled iOS Shortcut
that drops images into SCREENSHOT_WATCH_DIR through iCloud Drive sync) -- this
script watches that folder and asks Claude's vision to read who said what and
how many reactions/likes each message got, then inserts *suggested* aura_scores
rows for you to approve or edit in the admin UI. Nothing here talks to Instagram
directly; it only ever reads images you already have on disk.
"""

import base64
import json
import time
from pathlib import Path

from anthropic import Anthropic
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from . import config
from .db import SessionLocal, models

PROMPT = """This is a screenshot of a group chat. For each visible message, identify:
- the sender's display name
- a short excerpt of the message
- the number of likes/reactions/hearts shown on it (0 if none visible)

Return ONLY JSON: a list of objects with keys "sender", "excerpt", "reactions".
If you can't confidently read a field, omit that message rather than guessing."""


def analyze_screenshot(path: Path) -> list[dict]:
    client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    image_data = base64.standard_b64encode(path.read_bytes()).decode()
    media_type = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_data}},
                    {"type": "text", "text": PROMPT},
                ],
            }
        ],
    )
    text = response.content[0].text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return []


def name_to_user_id(db, sender_name: str) -> "str | None":
    user = db.query(models.User).filter(models.User.name.ilike(f"%{sender_name}%")).first()
    return user.id if user else None


def score_from_reactions(reactions: int) -> float:
    return float(reactions)  # tune scaling as you like once you see real data


def process_screenshot(path: Path):
    db = SessionLocal()
    try:
        entries = analyze_screenshot(path)
        for entry in entries:
            user_id = name_to_user_id(db, entry.get("sender", ""))
            if user_id is None:
                continue
            db.add(
                models.AuraScore(
                    user_id=user_id,
                    points=score_from_reactions(entry.get("reactions", 0)),
                    note=entry.get("excerpt"),
                    source_screenshot=str(path.name),
                    status=models.AuraScoreStatus.suggested,
                )
            )
        db.commit()
    finally:
        db.close()


class ScreenshotHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() not in (".png", ".jpg", ".jpeg"):
            return
        time.sleep(1)  # let the file finish syncing before reading it
        process_screenshot(path)


def watch():
    Path(config.SCREENSHOT_WATCH_DIR).mkdir(parents=True, exist_ok=True)
    observer = Observer()
    observer.schedule(ScreenshotHandler(), config.SCREENSHOT_WATCH_DIR, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    watch()
