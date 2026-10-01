"""Parse the Pass 3 family matrix out of AVAILABILITY_ARCHITECTURE.md.

The doc is the approved basis; parsing it (instead of retyping) keeps the manifest honest.
"""
from __future__ import annotations

import re
from common import ARCH_DOC


def _dex_numbers(text: str) -> list[int]:
    nums = []
    for part in text.split(","):
        part = part.strip()
        m = re.fullmatch(r"(\d+)\s*[–-]\s*(\d+)", part)
        if m:
            nums.extend(range(int(m.group(1)), int(m.group(2)) + 1))
        elif re.fullmatch(r"\d+", part):
            nums.append(int(part))
        else:
            raise ValueError(f"bad dex range: {part!r}")
    return nums


def parse_matrix() -> list[dict]:
    rows = []
    section = None
    in_matrix = False
    for line in ARCH_DOC.read_text().splitlines():
        if line.startswith("## 6."):
            in_matrix = True
        elif line.startswith("## 7."):
            in_matrix = False
        if not in_matrix:
            continue
        if line.startswith("### "):
            section = line[4:].strip()
            continue
        if not line.startswith("|") or line.startswith("|---") or line.startswith("| Family"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 8:
            continue
        name_dex = re.match(r"^(.*?)\s+((?:\d+(?:[–-]\d+)?)(?:,\d+(?:[–-]\d+)?)*)$", cells[0])
        if not name_dex:
            raise ValueError(f"cannot parse family cell: {cells[0]!r}")
        rows.append({
            "label": name_dex.group(1),
            "dex": _dex_numbers(name_dex.group(2)),
            "dex_text": name_dex.group(2),
            "origin_section": section,
            "earliest": cells[1],
            "area": cells[2],
            "entry_stage_text": cells[3],
            "tier": cells[4],
            "pre_e4": cells[5],
            "confidence": cells[6],
            "note": cells[7],
        })
    return rows


if __name__ == "__main__":
    r = parse_matrix()
    print(len(r), "rows")
