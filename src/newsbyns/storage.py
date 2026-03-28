from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from .config import STATE_FILE, ARCHIVE_DIR, MAX_SENT_SIGNATURES, MAX_TRANSLATION_CACHE
from .utils import iso_now

DEFAULT_STATE = {
    "sent_ids": [],
    "sent_signatures": [],
    "breaking_ids": [],
    "last_digest_hash": "",
    "last_run_iso": "",
    "last_breaking_run_iso": "",
    "translator_cache": {}
}

def load_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return DEFAULT_STATE.copy()
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return DEFAULT_STATE.copy()
    merged = DEFAULT_STATE.copy()
    merged.update(data)
    # keep shapes safe
    merged["sent_ids"] = list(dict.fromkeys(merged.get("sent_ids", [])))
    merged["sent_signatures"] = list(dict.fromkeys(merged.get("sent_signatures", [])))
    merged["breaking_ids"] = list(dict.fromkeys(merged.get("breaking_ids", [])))
    merged["translator_cache"] = dict(merged.get("translator_cache", {}))
    return merged

def save_state(state: dict[str, Any]) -> None:
    state["sent_ids"] = list(dict.fromkeys(state.get("sent_ids", [])))
    state["sent_signatures"] = list(dict.fromkeys(state.get("sent_signatures", [])))[-MAX_SENT_SIGNATURES:]
    state["breaking_ids"] = list(dict.fromkeys(state.get("breaking_ids", [])))[-MAX_SENT_SIGNATURES:]
    cache = dict(state.get("translator_cache", {}))
    if len(cache) > MAX_TRANSLATION_CACHE:
        keys = list(cache.keys())[-MAX_TRANSLATION_CACHE:]
        cache = {k: cache[k] for k in keys}
    state["translator_cache"] = cache
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

def write_archive(payload: dict) -> Path:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    stem = iso_now().replace(":", "-")
    path = ARCHIVE_DIR / f"run-{stem}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
