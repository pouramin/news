from __future__ import annotations
import hashlib
import re
from datetime import datetime, timezone
from dateutil import parser, tz

STOPWORDS = {
    "the", "a", "an", "on", "in", "at", "to", "for", "of", "and", "is", "are",
    "was", "were", "with", "as", "by", "from", "into", "after", "before",
    "amid", "over", "under", "against", "its", "their", "his", "her", "this",
    "that", "these", "those", "new", "report", "liveblog", "says"
}

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def now_local_str(zone_name: str = "Europe/Rome") -> str:
    local = now_utc().astimezone(tz.gettz(zone_name))
    return local.strftime("%H:%M %Z")

def iso_now() -> str:
    return now_utc().isoformat()

def parse_dt(value: str | None):
    if not value:
        return None
    try:
        dt = parser.parse(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None

def clean_ws(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()

def normalize_title(text: str) -> str:
    text = clean_ws(text).lower()
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    words = [w for w in text.split() if w not in STOPWORDS and len(w) > 1]
    return " ".join(words)

def stable_hash(*parts: str, n: int = 24) -> str:
    raw = "||".join(clean_ws(p) for p in parts if p)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:n]

def semantic_signature(title: str) -> str:
    normalized = normalize_title(title)
    return stable_hash(normalized, n=24)

def item_id_from_url_or_title(url: str, title: str, source: str) -> str:
    if url:
        return stable_hash(url, n=24)
    return stable_hash(normalize_title(title), source, n=24)

def hours_since(dt):
    if not dt:
        return None
    delta = now_utc() - dt.astimezone(timezone.utc)
    return max(delta.total_seconds() / 3600.0, 0.0)
