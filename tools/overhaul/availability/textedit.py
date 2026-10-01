"""Idempotently add messages to a res/text/<bank>.json file (same formatting as the repo's text tooling)."""
from __future__ import annotations

import json

from common import ROOT


def add_messages(bank: str, messages: dict[str, list[str] | str]) -> int:
    path = ROOT / "res" / "text" / f"{bank}.json"
    data = json.loads(path.read_text())
    have = {m["id"]: m for m in data["messages"]}
    added = 0
    for mid, text in messages.items():
        if mid in have:
            if have[mid]["en_US"] != text:
                raise SystemExit(f"{bank}:{mid} already exists with different text")
            continue
        data["messages"].append({"id": mid, "en_US": text})
        added += 1
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return added
