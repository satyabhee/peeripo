import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://peeripo:peeripo@localhost:5432/peeripo")

LIFE360_USERNAME = os.environ.get("LIFE360_USERNAME")
LIFE360_PASSWORD = os.environ.get("LIFE360_PASSWORD")
LIFE360_CIRCLE_NAME = os.environ.get("LIFE360_CIRCLE_NAME")

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
SCREENSHOT_WATCH_DIR = os.environ.get("SCREENSHOT_WATCH_DIR", "./screenshots")

_fernet_key = os.environ.get("TOKEN_ENCRYPTION_KEY")
fernet = Fernet(_fernet_key.encode()) if _fernet_key else None


def encrypt(value: str) -> str:
    if fernet is None:
        raise RuntimeError("TOKEN_ENCRYPTION_KEY not set")
    return fernet.encrypt(value.encode()).decode()


def decrypt(value: str) -> str:
    if fernet is None:
        raise RuntimeError("TOKEN_ENCRYPTION_KEY not set")
    return fernet.decrypt(value.encode()).decode()
