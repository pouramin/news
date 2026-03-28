from __future__ import annotations
from collections import defaultdict
from .fetchers import fetch_all
from .processor import enrich, semantic_dedupe, unseen_items, split_groups, pick_breaking, sort_items
from .storage import load_state, save_state, write_archive
from .telegram import build_breaking, build_digest, digest_hash, send_message
from .translator import translate_cached
from .utils import iso_now

def run():
    state = load_state()
    raw = fetch_all()
    enriched = enrich(raw)
    deduped = semantic_dedupe(enriched)
    fresh = unseen_items(deduped, state)
    fresh = sort_items(fresh)

    # translate only fresh titles, cached
    for item in fresh:
        item.title_fa = translate_cached(item.title, state)

    sent_now = []
    breaking_sent = []

    # breaking first
    for item in pick_breaking(fresh, state):
        send_message(build_breaking(item))
        state["breaking_ids"].append(item.item_id)
        state["sent_ids"].append(item.item_id)
        state["sent_signatures"].append(item.signature)
        breaking_sent.append(item)
        sent_now.append(item)

    remaining = [i for i in fresh if i.item_id not in set(state.get("sent_ids", []))]
    groups = split_groups(remaining)
    digest_items = []
    for key in ["military", "diplomatic", "economic", "minor"]:
        digest_items.extend(groups.get(key, []))

    d_hash = digest_hash(digest_items) if digest_items else ""
    digest_text = build_digest(groups) if digest_items else ""

    digest_sent = False
    if digest_items and digest_text and d_hash != state.get("last_digest_hash", ""):
        send_message(digest_text)
        digest_sent = True
        state["last_digest_hash"] = d_hash
        for item in digest_items:
            state["sent_ids"].append(item.item_id)
            state["sent_signatures"].append(item.signature)
            sent_now.append(item)

    state["last_run_iso"] = iso_now()
    if breaking_sent:
        state["last_breaking_run_iso"] = state["last_run_iso"]

    save_state(state)

    write_archive({
        "run_iso": state["last_run_iso"],
        "raw_count": len(raw),
        "enriched_count": len(enriched),
        "deduped_count": len(deduped),
        "fresh_count": len(fresh),
        "breaking_sent_count": len(breaking_sent),
        "digest_sent": digest_sent,
        "digest_item_count": len(digest_items),
        "sent_now_count": len(sent_now),
        "sent_now_ids": [i.item_id for i in sent_now],
        "remaining_unsent_count": max(len(fresh) - len(sent_now), 0),
    })

if __name__ == "__main__":
    run()
