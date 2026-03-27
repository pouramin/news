from __future__ import annotations
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
ARCHIVE_DIR = DATA_DIR / "archive"
STATE_PATH = DATA_DIR / "state.json"

APP_NAME = os.getenv("APP_NAME", "News By NS")
TIMEZONE_NAME = os.getenv("TIMEZONE_NAME", "Europe/Rome")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "")

MAX_ITEMS_PER_SECTION = int(os.getenv("MAX_ITEMS_PER_SECTION", "5"))
BREAKING_THRESHOLD = int(os.getenv("BREAKING_THRESHOLD", "80"))
DIGEST_THRESHOLD = int(os.getenv("DIGEST_THRESHOLD", "40"))
LOOKBACK_HOURS = int(os.getenv("LOOKBACK_HOURS", "30"))
MAX_AGE_HOURS = int(os.getenv("MAX_AGE_HOURS", "48"))


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


FEEDS = load_json(CONFIG_DIR / "feeds.json")
KEYWORDS = load_json(CONFIG_DIR / "keywords.json")
