from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def get_env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


OPENAI_API_KEY = get_env("OPENAI_API_KEY")
OPENAI_MODEL_TEXT = get_env("OPENAI_MODEL_TEXT", "gpt-4o-mini")
OPENAI_MODEL_VISION = get_env("OPENAI_MODEL_VISION", "gpt-4o-mini")

MONGODB_URI = get_env("MONGODB_URI")
MONGODB_DB_NAME = get_env("MONGODB_DB_NAME", "moodmate")

LASTFM_API_KEY = get_env("LASTFM_API_KEY")
