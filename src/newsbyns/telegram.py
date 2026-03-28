from __future__ import annotations
import hashlib
from typing import List
import requests
from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_CHANNEL_ID, MAX_ITEMS_PER_SECTION, MAX_MINOR_ITEMS, LOCAL_TZ
from .models import NewsItem
from .utils import now_local_str

CATEGORY_TITLES = {
    "military": "🔴 نظامی",
    "diplomatic": "🔵 دیپلماتیک",
    "economic": "🟢 اقتصادی",
}

def _escape(text: str) -> str:
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _targets() -> list[str]:
    targets = []
    if TELEGRAM_CHAT_ID:
        targets.append(TELEGRAM_CHAT_ID)
    if TELEGRAM_CHANNEL_ID and TELEGRAM_CHANNEL_ID not in targets:
        targets.append(TELEGRAM_CHANNEL_ID)
    return targets

def build_digest(groups: dict) -> str:
    lines: List[str] = [f"🕘 <b>News By NS</b> | {now_local_str(LOCAL_TZ)}", ""]
    total_added = 0
    for key in ["military", "diplomatic", "economic"]:
        items: List[NewsItem] = groups.get(key, [])[:MAX_ITEMS_PER_SECTION]
        if not items:
            continue
        lines.append(f"<b>{CATEGORY_TITLES[key]}</b>")
        for item in items:
            title = item.title_fa or item.title
            if item.title_fa and item.title_fa != item.title:
                lines.append(f"• [{item.score}] {_escape(title)}")
                lines.append(f"  EN: {_escape(item.title)}")
            else:
                lines.append(f"• [{item.score}] {_escape(title)}")
            lines.append(f"  منبع: {_escape(item.source)}")
            lines.append(f"  لینک: {item.url}")
            lines.append("")
            total_added += 1

    minor = groups.get("minor", [])[:MAX_MINOR_ITEMS]
    if minor:
        lines.append("<b>⚪️ نکات قابل توجه</b>")
        for item in minor:
            title = item.title_fa or item.title
            if item.title_fa and item.title_fa != item.title:
                lines.append(f"• [{item.score}] {_escape(title)}")
                lines.append(f"  EN: {_escape(item.title)}")
            else:
                lines.append(f"• [{item.score}] {_escape(title)}")
            lines.append(f"  منبع: {_escape(item.source)}")
            lines.append(f"  لینک: {item.url}")
            lines.append("")
            total_added += 1

    if total_added == 0:
        return ""
    return "\n".join(lines).strip()

def build_breaking(item: NewsItem) -> str:
    cat_map = {"military": "نظامی", "diplomatic": "دیپلماتیک", "economic": "اقتصادی"}
    category_fa = " / ".join(cat_map.get(x, x) for x in item.categories) if item.categories else "عمومی"
    title = item.title_fa or item.title
    lines = [
        "🚨 <b>خبر فوری | News By NS</b>",
        "",
        f"دسته: {category_fa}",
        f"امتیاز: {item.score}",
        f"منبع: {_escape(item.source)}",
        f"عنوان: {_escape(title)}",
    ]
    if item.title_fa and item.title_fa != item.title:
        lines.append(f"EN: {_escape(item.title)}")
    lines.append(f"لینک: {item.url}")
    return "\n".join(lines)

def digest_hash(items: list[NewsItem]) -> str:
    # time-independent hash: only content IDs/signatures
    raw = "|".join(sorted(f"{i.item_id}:{i.signature}:{i.score}" for i in items))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def send_message(text: str) -> list[dict]:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN")
    targets = _targets()
    if not targets:
        raise RuntimeError("Missing TELEGRAM_CHAT_ID / TELEGRAM_CHANNEL_ID")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    results = []
    for chat_id in targets:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        response = requests.post(url, data=payload, timeout=20)
        response.raise_for_status()
        results.append(response.json())
    return results
