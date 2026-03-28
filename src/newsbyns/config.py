import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
ARCHIVE_DIR = DATA_DIR / "archive"
CONFIG_DIR = ROOT / "config"
STATE_FILE = DATA_DIR / "state.json"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "").strip()

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "").strip()
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "").strip()

AZURE_TRANSLATOR_KEY = os.getenv("AZURE_TRANSLATOR_KEY", "").strip()
AZURE_TRANSLATOR_REGION = os.getenv("AZURE_TRANSLATOR_REGION", "").strip()
AZURE_TRANSLATOR_ENDPOINT = os.getenv("AZURE_TRANSLATOR_ENDPOINT", "https://api.cognitive.microsofttranslator.com").strip()

MAX_ITEMS_PER_SECTION = int(os.getenv("MAX_ITEMS_PER_SECTION", "5"))
MAX_MINOR_ITEMS = int(os.getenv("MAX_MINOR_ITEMS", "5"))
BREAKING_THRESHOLD = int(os.getenv("BREAKING_THRESHOLD", "88"))
MIN_DIGEST_SCORE = int(os.getenv("MIN_DIGEST_SCORE", "40"))
MAX_SENT_SIGNATURES = int(os.getenv("MAX_SENT_SIGNATURES", "4000"))
MAX_TRANSLATION_CACHE = int(os.getenv("MAX_TRANSLATION_CACHE", "2000"))

USER_AGENT = os.getenv("USER_AGENT", "NewsByNSBot/2.0 (+GitHub Actions)")
LOCAL_TZ = os.getenv("LOCAL_TZ", "Europe/Rome")

with (CONFIG_DIR / "keywords.json").open("r", encoding="utf-8") as f:
    KEYWORDS = json.load(f)

with (CONFIG_DIR / "feeds.json").open("r", encoding="utf-8") as f:
    FEEDS = json.load(f)
