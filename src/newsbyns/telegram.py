from __future__ import annotations
import hashlib
from typing import List

import requests

from .config import APP_NAME, MAX_ITEMS_PER_SECTION, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_CHANNEL_ID
from .models import NewsItem
from .utils import now_local_str

CATEGORY_TITLES = {
    "military": "🔴 نظامی",
    "diplomatic": "🔵 دیپلماتیک",
    "economic": "🟢 اقتصادی",
}


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _sectioned_items(groups: dict[str, list[NewsItem]]) -> list[NewsItem]:
    used_ids = set()
    ordered: list[NewsItem] = []

    for key in ["military", "diplomatic", "economic"]:
        count = 0
        for item in groups.get(key, []):
            if item.item_id in used_ids:
                continue
            ordered.append(item)
            used_ids.add(item.item_id)
            count += 1
            if count >= MAX_ITEMS_PER_SECTION:
                break

    for item in groups.get("minor", []):
        if item.item_id in used_ids:
            continue
        ordered.append(item)
        used_ids.add(item.item_id)
        if len([x for x in ordered if x.primary_category() == "minor"]) >= 5:
            break

    return ordered


def build_digest(groups: dict[str, list[NewsItem]]) -> str:
    lines: List[str] = [f"🕘 <b>{_escape(APP_NAME)}</b> | {now_local_str()}", ""]
    used_ids = set()
    total = 0

    for key in ["military", "diplomatic", "economic"]:
        section = []
        for item in groups.get(key, []):
            if item.item_id in used_ids:
                continue
            section.append(item)
            used_ids.add(item.item_id)
            if len(section) >= MAX_ITEMS_PER_SECTION:
                break
        if not section:
            continue
        lines.append(f"<b>{CATEGORY_TITLES[key]}</b>")
        for item in section:
            lines.append(f"• [{item.score}] {_escape(item.title)}")
            lines.append(f"  منبع: {_escape(item.source)}")
            lines.append(f"  لینک: {item.url}")
            lines.append("")
            total += 1

    minor = [x for x in groups.get("minor", []) if x.item_id not in used_ids][:5]
    if minor:
        lines.append("<b>⚪️ نکات قابل توجه</b>")
        for item in minor:
            lines.append(f"• [{item.score}] {_escape(item.title)}")
            lines.append(f"  منبع: {_escape(item.source)}")
            lines.append(f"  لینک: {item.url}")
            lines.append("")
            total += 1

    if total == 0:
        lines.append("خبر قابل توجه تازه‌ای در این اجرا پیدا نشد.")
    return "\n".join(lines).strip()


def build_breaking(item: NewsItem) -> str:
    cat_map = {"military": "نظامی", "diplomatic": "دیپلماتیک", "economic": "اقتصادی", "minor": "عمومی"}
    cats = " / ".join(cat_map.get(c, c) for c in item.categories) if item.categories else "عمومی"
    return "\n".join([
        f"🚨 <b>خبر فوری | {_escape(APP_NAME)}</b>",
        "",
        f"دسته: {cats}",
        f"امتیاز: {item.score}",
        f"منبع: {_escape(item.source)}",
        f"عنوان: {_escape(item.title)}",
        f"لینک: {item.url}",
    ])


def digest_hash(groups: dict[str, list[NewsItem]]) -> str:
    items = _sectioned_items(groups)
    raw = "|".join(f"{item.item_id}:{item.score}" for item in items)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _targets() -> list[str]:
    targets = []
    if TELEGRAM_CHAT_ID:
        targets.append(TELEGRAM_CHAT_ID)
    if TELEGRAM_CHANNEL_ID and TELEGRAM_CHANNEL_ID not in targets:
        targets.append(TELEGRAM_CHANNEL_ID)
    return targets


def send_message(text: str) -> list[dict]:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN")
    targets = _targets()
    if not targets:
        raise RuntimeError("Missing TELEGRAM_CHAT_ID / TELEGRAM_CHANNEL_ID")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    out = []
    for chat_id in targets:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        res = requests.post(url, data=payload, timeout=20)
        res.raise_for_status()
        out.append(res.json())
    return out
