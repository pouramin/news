from __future__ import annotations
import hashlib
import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from dateutil import parser as date_parser

from .config import TIMEZONE_NAME


TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = TAG_RE.sub(" ", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = SPACE_RE.sub(" ", text).strip()
    return text


def stable_id(source: str, title: str, url: str) -> str:
    raw = f"{source}|{title.strip().lower()}|{url.strip()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def parse_dt(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    dt = date_parser.parse(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def now_local_str() -> str:
    return datetime.now(ZoneInfo(TIMEZONE_NAME)).strftime("%H:%M %Z")


def now_iso_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def hours_ago(hours: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(hours=hours)
