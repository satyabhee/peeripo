import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.database import SessionLocal  # noqa: E402
from app import models  # noqa: E402

__all__ = ["SessionLocal", "models"]
