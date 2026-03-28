from __future__ import annotations
import requests
import feedparser
from typing import Iterable, List
from .config import FEEDS, NEWSAPI_KEY, GNEWS_API_KEY, USER_AGENT
from .models import NewsItem
from .utils import parse_dt, clean_ws

HEADERS = {"User-Agent": USER_AGENT}

def fetch_rss() -> List[NewsItem]:
    items: List[NewsItem] = []
    for feed in FEEDS.get("rss", []):
        source = feed.get("source", "Unknown")
        url = feed.get("url")
        if not url:
            continue
        try:
            parsed = feedparser.parse(url, request_headers=HEADERS)
        except Exception:
            continue
        for entry in parsed.entries[:20]:
            title = clean_ws(entry.get("title", ""))
            link = clean_ws(entry.get("link", ""))
            summary = clean_ws(entry.get("summary", "") or entry.get("description", ""))
            published = parse_dt(entry.get("published") or entry.get("updated"))
            if not title or not link:
                continue
            items.append(NewsItem(source=source, title=title, url=link, summary=summary, published_at=published))
    return items

def fetch_newsapi() -> List[NewsItem]:
    if not NEWSAPI_KEY:
        return []
    query = "Iran OR Israel OR Lebanon OR Hezbollah OR Houthis OR Yemen OR Syria OR Iraq OR Hormuz"
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 20,
        "apiKey": NEWSAPI_KEY,
    }
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=25)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return []
    out = []
    for art in data.get("articles", [])[:20]:
        title = clean_ws(art.get("title", ""))
        link = clean_ws(art.get("url", ""))
        if not title or not link:
            continue
        out.append(
            NewsItem(
                source=clean_ws((art.get("source") or {}).get("name", "NewsAPI")),
                title=title,
                url=link,
                summary=clean_ws(art.get("description", "") or ""),
                published_at=parse_dt(art.get("publishedAt")),
            )
        )
    return out

def fetch_gnews() -> List[NewsItem]:
    if not GNEWS_API_KEY:
        return []
    url = "https://gnews.io/api/v4/search"
    params = {
        "q": "Iran OR Israel OR Lebanon OR Hezbollah OR Houthis OR Yemen OR Syria OR Iraq OR Hormuz",
        "lang": "en",
        "max": 20,
        "token": GNEWS_API_KEY,
    }
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=25)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return []
    out = []
    for art in data.get("articles", [])[:20]:
        title = clean_ws(art.get("title", ""))
        link = clean_ws(art.get("url", ""))
        if not title or not link:
            continue
        out.append(
            NewsItem(
                source=clean_ws((art.get("source") or {}).get("name", "GNews")),
                title=title,
                url=link,
                summary=clean_ws(art.get("description", "") or ""),
                published_at=parse_dt(art.get("publishedAt")),
            )
        )
    return out

def fetch_all() -> List[NewsItem]:
    items: List[NewsItem] = []
    for getter in (fetch_rss, fetch_newsapi, fetch_gnews):
        items.extend(getter())
    return items
