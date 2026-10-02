#!/usr/bin/env python3
"""Validate the source/runtime contract for field-light archive IDs."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORDER = ROOT / "res/field/lighting/lighting_sets.order"
HEADER = ROOT / "include/constants/field/area_light.h"
AREA_DIR = ROOT / "res/field/area_data"


def main() -> int:
    names = [line.strip() for line in ORDER.read_text().splitlines() if line.strip()]
    expected = [f"lighting_set_{i:03d}" for i in range(len(names))]
    if names != expected:
        raise SystemExit(
            "lighting_sets.order must be contiguous and index-stable: "
            f"expected {expected}, got {names}"
        )

    header = HEADER.read_text(encoding="utf-8")
    enum_body_match = re.search(
        r"enum\s+AreaLightArchiveID\s*\{(?P<body>.*?)\};", header, re.S
    )
    if enum_body_match is None:
        raise SystemExit("AreaLightArchiveID enum not found")
    body = enum_body_match.group("body")
    entries = [
        line.split("//", 1)[0].strip().rstrip(",")
        for line in body.splitlines()
        if line.strip() and not line.lstrip().startswith("//")
    ]
    count_index = next(
        (i for i, entry in enumerate(entries) if entry.startswith("AREA_LIGHT_SET_COUNT")),
        None,
    )
    if count_index is None:
        raise SystemExit("AREA_LIGHT_SET_COUNT missing")
    if count_index != len(names):
        raise SystemExit(
            f"AREA_LIGHT_SET_COUNT resolves to {count_index}, but lighting archive has "
            f"{len(names)} members"
        )

    bad: list[str] = []
    referenced: set[int] = set()
    for path in sorted(AREA_DIR.glob("area_data_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        value = data["lightingSet"]
        match = re.fullmatch(r"lighting_set_(\d{3})", value)
        if match is None:
            bad.append(f"{path.name}: malformed lightingSet {value!r}")
            continue
        index = int(match.group(1))
        referenced.add(index)
        if index >= len(names):
            bad.append(
                f"{path.name}: {value} is outside lighting archive size {len(names)}"
            )

    if bad:
        raise SystemExit("\n".join(bad))

    print(
        f"PASS: {len(names)} lighting archive members; "
        f"AREA_LIGHT_SET_COUNT={count_index}; "
        f"{len(referenced)} lighting IDs referenced by area data"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
