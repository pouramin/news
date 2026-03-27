from __future__ import annotations
from datetime import datetime

from .fetchers import fetch_all_items
from .pipeline import process_items
from .storage import archive_payload, load_state, save_state
from .telegram import build_breaking, build_digest, digest_hash, send_message
from .utils import now_iso_utc


ORDERED_KEYS = ["military", "diplomatic", "economic", "minor"]


def _only_unsent(groups, sent_ids: set[str]) -> dict[str, list]:
    return {
        key: [item for item in groups.get(key, []) if item.item_id not in sent_ids]
        for key in ORDERED_KEYS
    }


def main() -> None:
    state = load_state()
    sent_ids = set(state.get("sent_ids", []))
    breaking_ids = set(state.get("breaking_ids", []))

    fetched = fetch_all_items()
    groups = process_items(fetched)

    # Send breaking alerts only once, and mark them as already sent
    new_breaking = []
    for key in ["military", "diplomatic", "economic"]:
        for item in groups.get(key, []):
            if item.is_breaking and item.item_id not in breaking_ids:
                new_breaking.append(item)

    for item in new_breaking[:5]:
        send_message(build_breaking(item))
        breaking_ids.add(item.item_id)
        sent_ids.add(item.item_id)

    # Build digest only from truly unseen items
    unsent_groups = _only_unsent(groups, sent_ids)
    unsent_present = any(unsent_groups.get(key) for key in ORDERED_KEYS)
    current_hash = digest_hash(unsent_groups)

    if unsent_present and current_hash != state.get("last_digest_hash", ""):
        digest_text = build_digest(unsent_groups)
        send_message(digest_text)
        for key in ORDERED_KEYS:
            for item in unsent_groups.get(key, []):
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
            "unsent_group_counts": {k: len(v) for k, v in unsent_groups.items()},
            "new_breaking_ids": [x.item_id for x in new_breaking],
            "digest_hash": current_hash,
            "state_sent_ids_count": len(state["sent_ids"]),
            "state_breaking_ids_count": len(state["breaking_ids"]),
        },
    )


if __name__ == "__main__":
    main()
