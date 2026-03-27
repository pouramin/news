from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from typing import Iterable

from .config import BREAKING_THRESHOLD, DIGEST_THRESHOLD, KEYWORDS, MAX_AGE_HOURS
from .models import NewsItem


def _contains_any(text: str, keywords: list[str]) -> int:
    text_l = text.lower()
    return sum(1 for kw in keywords if kw.lower() in text_l)


def is_relevant(item: NewsItem) -> bool:
    text = f"{item.title} {item.summary}".lower()
    region_hits = _contains_any(text, KEYWORDS["region"])
    noise_hits = _contains_any(text, KEYWORDS.get("negative_noise", []))
    return region_hits > 0 and noise_hits == 0


def classify(item: NewsItem) -> None:
    text = f"{item.title} {item.summary}".lower()
    categories = []
    if _contains_any(text, KEYWORDS["military"]):
        categories.append("military")
    if _contains_any(text, KEYWORDS["diplomatic"]):
        categories.append("diplomatic")
    if _contains_any(text, KEYWORDS["economic"]):
        categories.append("economic")
    item.categories = categories or ["minor"]


def score(item: NewsItem) -> None:
    text = f"{item.title} {item.summary}".lower()
    score = 0
    region_hits = _contains_any(text, KEYWORDS["region"])
    military_hits = _contains_any(text, KEYWORDS["military"])
    diplomatic_hits = _contains_any(text, KEYWORDS["diplomatic"])
    economic_hits = _contains_any(text, KEYWORDS["economic"])

    score += min(region_hits * 8, 24)
    score += min(military_hits * 10, 30)
    score += min(diplomatic_hits * 8, 24)
    score += min(economic_hits * 8, 24)

    src = item.source.lower()
    if "reuters" in src or "ap" in src or "bbc" in src:
        score += 12
    elif "al jazeera" in src or "defense" in src:
        score += 8
    else:
        score += 5

    age_hours = max((datetime.now(timezone.utc) - item.published_at).total_seconds() / 3600, 0)
    if age_hours <= 2:
        score += 15
    elif age_hours <= 6:
        score += 10
    elif age_hours <= 12:
        score += 6
    elif age_hours > 24:
        score -= 10

    if any(k in text for k in ["breaking", "urgent", "live updates"]):
        score += 8

    item.score = max(0, min(100, score))
    item.is_breaking = item.score >= BREAKING_THRESHOLD and item.primary_category() in {"military", "diplomatic", "economic"}


def dedupe_similar(items: list[NewsItem]) -> list[NewsItem]:
    seen = set()
    out = []
    for item in sorted(items, key=lambda x: (x.published_at, x.score), reverse=True):
        key = " ".join(item.title.lower().split()[:10])
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def process_items(items: list[NewsItem]) -> dict[str, list[NewsItem]]:
    filtered = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=MAX_AGE_HOURS)
    for item in items:
        if item.published_at < cutoff:
            continue
        if not is_relevant(item):
            continue
        classify(item)
        score(item)
        if item.score >= DIGEST_THRESHOLD:
            filtered.append(item)
        elif item.primary_category() == "minor" and item.score >= 25:
            filtered.append(item)

    filtered = dedupe_similar(filtered)

    groups = defaultdict(list)
    for item in sorted(filtered, key=lambda x: (x.score, x.published_at), reverse=True):
        groups[item.primary_category()].append(item)
    for key in ["military", "diplomatic", "economic", "minor"]:
        groups[key] = groups.get(key, [])
    return groups
