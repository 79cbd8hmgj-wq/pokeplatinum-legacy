"""Shared helpers for the D5 Legendary/Mythical event tooling."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVENTS_DIR = ROOT / "docs" / "overhaul" / "implementation" / "events"


def add_messages(bank: str, messages: dict[str, list[str] | str]) -> int:
    """Idempotently append messages to res/text/<bank>.json (repo formatting: indent 2)."""
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
