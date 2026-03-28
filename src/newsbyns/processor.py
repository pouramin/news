from __future__ import annotations
from collections import defaultdict
from typing import Iterable, List, Dict
from .config import KEYWORDS, BREAKING_THRESHOLD, MIN_DIGEST_SCORE
from .models import NewsItem
from .utils import (
    clean_ws, semantic_signature, item_id_from_url_or_title,
    hours_since, normalize_title
)

def _contains_any(text: str, words: list[str]) -> int:
    t = text.lower()
    return sum(1 for w in words if w.lower() in t)

def _eligible(text: str) -> bool:
    text = text.lower()
    if _contains_any(text, KEYWORDS.get("ignore", [])):
        return False
    return _contains_any(text, KEYWORDS.get("must_have", [])) > 0

def enrich(items: Iterable[NewsItem]) -> List[NewsItem]:
    out: List[NewsItem] = []
    for item in items:
        fulltext = clean_ws(f"{item.title} {item.summary}")
        if not _eligible(fulltext):
            continue

        signature = semantic_signature(item.title)
        item.signature = signature
        item.item_id = item_id_from_url_or_title(item.url, item.title, item.source)

        # category scoring
        m = _contains_any(fulltext, KEYWORDS.get("military", []))
        d = _contains_any(fulltext, KEYWORDS.get("diplomatic", []))
        e = _contains_any(fulltext, KEYWORDS.get("economic", []))

        cats = []
        if m > 0:
            cats.append("military")
        if d > 0:
            cats.append("diplomatic")
        if e > 0:
            cats.append("economic")
        item.categories = cats or ["minor"]

        score = 10
        score += m * 9 + d * 6 + e * 7
        score += _contains_any(fulltext, KEYWORDS.get("breaking_bonus", [])) * 10

        hs = hours_since(item.published_at)
        if hs is not None:
            if hs <= 2:
                score += 18
            elif hs <= 6:
                score += 12
            elif hs <= 12:
                score += 7
            elif hs <= 24:
                score += 2
            else:
                score -= 8

        if "liveblog" in item.url.lower() or "live blog" in item.title.lower():
            score -= 6

        # source weighting
        src = item.source.lower()
        if "reuters" in src or "bbc" in src or "al jazeera" in src:
            score += 6
        if "times of israel" in src or "jerusalem post" in src:
            score += 3

        # boost for Iran-first relevance
        if any(x in fulltext.lower() for x in ["iran", "iranian", "tehran", "hormuz", "irgc"]):
            score += 8

        item.score = max(min(score, 99), 0)
        item.reason = f"m={m}, d={d}, e={e}, recency={hs}"
        out.append(item)
    return out

def semantic_dedupe(items: Iterable[NewsItem]) -> List[NewsItem]:
    best_by_signature: dict[str, NewsItem] = {}
    for item in items:
        existing = best_by_signature.get(item.signature)
        if existing is None or item.score > existing.score:
            best_by_signature[item.signature] = item
    return list(best_by_signature.values())

def unseen_items(items: Iterable[NewsItem], state: dict) -> List[NewsItem]:
    sent_ids = set(state.get("sent_ids", []))
    sent_signatures = set(state.get("sent_signatures", []))
    out = []
    for item in items:
        if item.item_id in sent_ids:
            continue
        if item.signature in sent_signatures:
            continue
        out.append(item)
    return out

def sort_items(items: Iterable[NewsItem]) -> List[NewsItem]:
    return sorted(items, key=lambda x: (x.score, x.published_at.isoformat() if x.published_at else ""), reverse=True)

def split_groups(items: Iterable[NewsItem]) -> Dict[str, List[NewsItem]]:
    groups = defaultdict(list)
    for item in sort_items(items):
        primary = item.categories[0] if item.categories else "minor"
        if primary not in {"military", "diplomatic", "economic"}:
            primary = "minor"
        if item.score < MIN_DIGEST_SCORE and primary != "minor":
            groups["minor"].append(item)
        else:
            groups[primary].append(item)
    return groups

def pick_breaking(items: Iterable[NewsItem], state: dict) -> List[NewsItem]:
    already = set(state.get("breaking_ids", []))
    out = []
    for item in sort_items(items):
        if item.score >= BREAKING_THRESHOLD and item.item_id not in already:
            out.append(item)
    return out
