#!/usr/bin/env python3
"""Validate G7.4 core-menu refresh (Party, Summary, Bag, Start, Shop).

Checks, against the pre-G7.4 baseline commit:
  * touched PNGs keep size/mode (cell/OAM contract) and use only indices 0-15;
  * touched palettes keep their header/entry count and only the allowed entries differ;
  * every generator is idempotent (a second run changes no byte).
"""

import hashlib
import io
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
G = ROOT / "res" / "graphics"
BASELINE = "d7c1ec09"

PNGS = [
    "party_menu/cursor.png", "party_menu/button.png",
    "pokemon_summary_screen/tab_arrow.png", "pokemon_summary_screen/move_cursor.png",
    "start_menu/cursor.png",
]
# palette -> set of entry indices allowed to differ from baseline
PALS = {
    "party_menu/shared.pal": set(),  # banks 0/1 are regenerated, must stay stable
    "pokemon_summary_screen/tiles_main.pal": {b * 16 + o for b in range(10) for o in (2, 15)},
    "bag/bag_ui_main.pal": {3, 4, 5},
    "bag/ui_elements.pal": {1, 4},
    "shop_menu/default.pal": {6, 7, 8},
    "shop_menu/frontier.pal": {6, 7, 8},
    "shop_menu/sprites.pal": {1, 4},
}
GENERATORS = ["party_menu", "summary", "bag", "start_menu", "shop"]
failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)


def baseline(path):
    return subprocess.run(["git", "show", f"{BASELINE}:res/graphics/{path}"], cwd=ROOT,
                          capture_output=True, check=True).stdout


def entries(raw):
    lines = raw.decode().replace("\r", "").split("\n")
    return lines[:3], [l for l in lines[3:] if l]


def snapshot():
    return {p: hashlib.sha256((G / p).read_bytes()).hexdigest() for p in PNGS + list(PALS)}


def main():
    for p in PNGS:
        old = Image.open(io.BytesIO(baseline(p)))
        new = Image.open(G / p)
        check(old.size == new.size and old.mode == new.mode == "P", f"{p}: size/mode changed")
        check(max(new.tobytes()) <= 15, f"{p}: index >15")
    for p, allowed in PALS.items():
        oh, oe = entries(baseline(p))
        nh, ne = entries((G / p).read_bytes())
        check(oh == nh and len(oe) == len(ne), f"{p}: header/count changed")
        for i, (a, b) in enumerate(zip(oe, ne)):
            check(a == b or i in allowed, f"{p}: entry {i} changed unexpectedly ({a} -> {b})")
    before = snapshot()
    for g in GENERATORS:
        subprocess.run([sys.executable, str(ROOT / f"tools/visual_overhaul/generate_{g}_ui.py")], check=True)
    check(before == snapshot(), "generator rerun changed output (not idempotent)")
    if failures:
        print("\n".join(failures))
        return 1
    print("G7.4 core menu validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
