from __future__ import annotations
from datetime import datetime

from .fetchers import fetch_all_items
from .pipeline import process_items
from .storage import archive_payload, load_state, save_state
from .telegram import build_breaking, build_digest, digest_hash, send_message
from .utils import now_iso_utc


def main() -> None:
    state = load_state()
    sent_ids = set(state.get("sent_ids", []))
    breaking_ids = set(state.get("breaking_ids", []))

    fetched = fetch_all_items()
    groups = process_items(fetched)

    # Breaking alerts first
    new_breaking = []
    for key in ["military", "diplomatic", "economic"]:
        for item in groups.get(key, []):
            if item.is_breaking and item.item_id not in breaking_ids:
                new_breaking.append(item)

    for item in new_breaking[:5]:
        send_message(build_breaking(item))
        breaking_ids.add(item.item_id)

    # Digest only if there is at least one unsent item in the digest groups
    unsent_present = False
    for key in ["military", "diplomatic", "economic", "minor"]:
        for item in groups.get(key, []):
            if item.item_id not in sent_ids:
                unsent_present = True
                break
        if unsent_present:
            break

    digest_text = build_digest(groups)
    current_hash = digest_hash(digest_text)

    if unsent_present and current_hash != state.get("last_digest_hash", ""):
        send_message(digest_text)
        for key in ["military", "diplomatic", "economic", "minor"]:
            for item in groups.get(key, []):
                sent_ids.add(item.item_id)
        state["last_digest_hash"] = current_hash

    state["sent_ids"] = sorted(sent_ids)[-5000:]
    state["breaking_ids"] = sorted(breaking_ids)[-5000:]
    state["last_run_iso"] = now_iso_utc()
    save_state(state)

    archive_payload(
        datetime.utcnow().strftime("run_%Y%m%d_%H%M%S"),
        {
            "fetched_count": len(fetched),
            "group_counts": {k: len(v) for k, v in groups.items()},
            "new_breaking_ids": [x.item_id for x in new_breaking],
            "digest_hash": current_hash,
        },
    )


if __name__ == "__main__":
    main()
