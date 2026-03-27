from __future__ import annotations
from datetime import datetime, timezone
from typing import Iterable, List

import feedparser
import requests

from .config import FEEDS, GNEWS_API_KEY, LOOKBACK_HOURS, NEWSAPI_KEY
from .models import NewsItem
from .utils import clean_text, hours_ago, parse_dt, stable_id


HEADERS = {"User-Agent": "NewsByNS/1.0"}


def fetch_rss_items() -> List[NewsItem]:
    items: list[NewsItem] = []
    cutoff = hours_ago(LOOKBACK_HOURS)
    for feed in FEEDS.get("rss", []):
        try:
            parsed = feedparser.parse(feed["url"], request_headers=HEADERS)
        except Exception:
            continue
        for entry in parsed.entries[:30]:
            title = clean_text(getattr(entry, "title", ""))
            url = getattr(entry, "link", "")
            summary = clean_text(getattr(entry, "summary", ""))
            published_raw = (
                getattr(entry, "published", None)
                or getattr(entry, "updated", None)
                or getattr(entry, "created", None)
            )
            published_at = parse_dt(published_raw)
            if published_at < cutoff:
                continue
            if not title or not url:
                continue
            items.append(
                NewsItem(
                    item_id=stable_id(feed["name"], title, url),
                    title=title,
                    url=url,
                    source=feed["name"],
                    published_at=published_at,
                    summary=summary,
                )
            )
    return items


def _newsapi_request(url: str, params: dict) -> dict | None:
    try:
        res = requests.get(url, params=params, headers=HEADERS, timeout=20)
        if not res.ok:
            return None
        return res.json()
    except Exception:
        return None


def fetch_newsapi_items() -> List[NewsItem]:
    if not NEWSAPI_KEY:
        return []
    q = '(Iran OR Israel OR Gaza OR Lebanon OR Syria OR Iraq OR Yemen OR Houthi OR "Middle East" OR "Red Sea" OR Hormuz)'
    data = _newsapi_request(
        "https://newsapi.org/v2/everything",
        {
            "apiKey": NEWSAPI_KEY,
            "q": q,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 25,
        },
    )
    if not data or not data.get("articles"):
        return []
    cutoff = hours_ago(LOOKBACK_HOURS)
    items: list[NewsItem] = []
    for article in data["articles"]:
        title = clean_text(article.get("title", ""))
        url = article.get("url", "")
        summary = clean_text(article.get("description", "") or article.get("content", ""))
        published_at = parse_dt(article.get("publishedAt"))
        if published_at < cutoff or not title or not url:
            continue
        source = clean_text((article.get("source") or {}).get("name", "NewsAPI")) or "NewsAPI"
        items.append(NewsItem(stable_id(source, title, url), title, url, source, published_at, summary=summary))
    return items


def fetch_gnews_items() -> List[NewsItem]:
    if not GNEWS_API_KEY:
        return []
    data = _newsapi_request(
        "https://gnews.io/api/v4/search",
        {
            "apikey": GNEWS_API_KEY,
            "q": 'Iran OR Israel OR Gaza OR Lebanon OR Syria OR Iraq OR Yemen OR Houthi OR "Middle East" OR "Red Sea" OR Hormuz',
            "lang": "en",
            "max": 20,
        },
    )
    if not data or not data.get("articles"):
        return []
    cutoff = hours_ago(LOOKBACK_HOURS)
    items: list[NewsItem] = []
    for article in data["articles"]:
        title = clean_text(article.get("title", ""))
        url = article.get("url", "")
        summary = clean_text(article.get("description", ""))
        published_at = parse_dt(article.get("publishedAt"))
        if published_at < cutoff or not title or not url:
            continue
        source = clean_text((article.get("source") or {}).get("name", "GNews")) or "GNews"
        items.append(NewsItem(stable_id(source, title, url), title, url, source, published_at, summary=summary))
    return items


def fetch_all_items() -> list[NewsItem]:
    all_items = []
    all_items.extend(fetch_rss_items())
    all_items.extend(fetch_newsapi_items())
    all_items.extend(fetch_gnews_items())
    # Deduplicate raw fetched items by ID while keeping newest summary-rich copy.
    merged: dict[str, NewsItem] = {}
    for item in all_items:
        prev = merged.get(item.item_id)
        if prev is None or (len(item.summary) > len(prev.summary)):
            merged[item.item_id] = item
    return list(merged.values())
