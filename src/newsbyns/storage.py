from __future__ import annotations
import json
from pathlib import Path
from typing import Any

from .config import ARCHIVE_DIR, DATA_DIR, STATE_PATH
from .utils import now_iso_utc


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    if not STATE_PATH.exists():
        save_state({"sent_ids": [], "breaking_ids": [], "last_digest_hash": "", "last_run_iso": ""})


def load_state() -> dict[str, Any]:
    ensure_dirs()
    with STATE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict[str, Any]) -> None:
    ensure_dirs()
    with STATE_PATH.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def archive_payload(name: str, payload: dict[str, Any]) -> Path:
    ensure_dirs()
    path = ARCHIVE_DIR / f"{name}.json"
    payload = {**payload, "archived_at": now_iso_utc()}
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path
