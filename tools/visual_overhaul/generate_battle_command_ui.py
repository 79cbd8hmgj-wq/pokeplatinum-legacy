#!/usr/bin/env python3
"""G7.1A/B battle command-center generator.

Owner of the visual treatment of the battle bottom-screen command menu
(Fight / Bag / Pokemon / Run), the shared sub-screen "deck" backdrop and the
muted empty-slot ramp used by the move-select menu.

All art lives inside the prebuilt ``res/prebuilt/battle/graphic/pl_batt_bg.narc``
(Nitro NCGR / NCLR / NSCR members).  This script rewrites only the members
listed below and is idempotent: it never derives output from the current
state of an edited member, so re-running it produces no diff.

Resource contract (unchanged by this tool)
  * NARC member count / order / sizes of all untouched members
  * tile member 28 and every tilemap member are not modified (palette-only
    restyle; tile art and geometry stay retail)
  * palette banks keep their index semantics (0 = transparent key)
  * touch rectangles, cell/OAM data and C sources are not touched
"""

import argparse
import colorsys
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from nitro_narc import (  # noqa: E402
    bgr555,
    nclr_colors,
    nclr_set_colors,
    read_narc,
    write_narc,
)

ROOT = Path(__file__).resolve().parents[2]
NARC_PATH = ROOT / "res" / "prebuilt" / "battle" / "graphic" / "pl_batt_bg.narc"

PALETTE_MAIN = 242  # all 16 banks, used by every non-Frontier sub-screen

# (terrain palette member, speed-up palette member, retail hue deg, retail sat)
# Members come from sSubscreenBgPlttIndices in battle_subscreen.c.  Hue and
# saturation are recorded from the retail palettes (entry 11) so the script
# does not depend on the current state of the archive.
TERRAIN_DECKS = (
    (0xF3, 0x10B, 84, 0.16),
    (0xF4, 0x10C, 210, 0.20),
    (0xF5, 0x10D, 169, 0.20),
    (0xF6, 0x10E, 105, 0.22),
    (0xF7, 0x10F, 23, 0.18),
    (0xF8, 0x110, 259, 0.11),
    (0xF9, 0x111, 218, 0.00),
    (0xFA, 0x112, 48, 0.17),
    (0xFB, 0x113, 60, 0.14),
    (0xFC, 0x114, 268, 0.11),
    (0xFD, 0x115, 252, 0.28),
    (0xFE, 0x116, 240, 0.28),
    (0xFF, 0x117, 130, 0.32),
    (0x100, 0x118, 45, 0.38),
    (0x101, 0x119, 17, 0.81),
    (0x102, 0x11A, 326, 0.61),
    (0x103, 0x11B, 300, 0.16),
    (0x11C, 0x11D, 236, 0.85),
)
DEFAULT_DECK = (218, 0.00)

# Backdrop roles inside palette bank 0 (tilemap 0x31 / tile member 28):
#   11 field, 14 header/footer bands, 12/13 band edge lines,
#   9 emblem ring, 15 emblem fill, 10/8 minor fill.
DECK_NORMAL = {11: 0.17, 14: 0.09, 12: 0.40, 13: 0.28, 9: 0.33, 15: 0.25, 10: 0.20, 8: 0.15}
DECK_SPEED = {11: 0.27, 14: 0.15, 12: 0.52, 13: 0.40, 9: 0.46, 15: 0.36, 10: 0.30, 8: 0.24}


def hsv_color(hue, sat, val):
    r, g, b = colorsys.hsv_to_rgb(hue / 360.0, min(sat, 1.0), min(val, 1.0))
    return bgr555((round(r * 255), round(g * 255), round(b * 255)))


def deck_palette(hue, retail_sat, roles, sat_boost=1.0):
    sat = min(0.28 + 0.35 * retail_sat, 0.60) * sat_boost
    updates = {}
    for index, val in roles.items():
        scale = 0.9 if index == 14 else 0.7 if index in (12, 9) else 1.0
        updates[index] = hsv_color(hue, sat * scale, val)
    return updates


def rgb(value):
    return bgr555(((value >> 16) & 255, (value >> 8) & 255, value & 255))


# Command key banks (main palette, bank = index // 16).  Entry semantics:
# 1 white, 2..9 light -> dark ramp, 10 structural outline.  Entries 11-15
# (accent, greys, black) keep their retail values except where listed.
# Bank 14 is the muted "empty / unavailable slot" ramp used for empty move
# slots and cleared target slots (G7.1B); banks 1-4 are the G7.1A keys.
ACTION_BANKS = {
    1: {  # Fight - hot crimson
        2: 0xFFD4CC, 3: 0xFF9C8C, 4: 0xFF6258, 5: 0xE8302C,
        6: 0xC0242C, 7: 0x8C1C34, 8: 0x5C1430, 9: 0xFFB4A8, 10: 0x0A1230,
    },
    2: {  # Bag - amber
        2: 0xFFF0C0, 3: 0xFFD060, 4: 0xFFB020, 5: 0xF09A18,
        6: 0xC87414, 7: 0x985010, 8: 0x683410, 9: 0xFFE48C, 10: 0x0A1230,
    },
    3: {  # Pokemon - emerald
        2: 0xD8FFD0, 3: 0x80F060, 4: 0x50D038, 5: 0x38B830,
        6: 0x2C9028, 7: 0x1F6C24, 8: 0x144C20, 9: 0xB8F8A0, 10: 0x0A1230,
    },
    4: {  # Run - azure
        2: 0xD0F0FF, 3: 0x58D0FF, 4: 0x28B0F8, 5: 0x1C8CDC,
        6: 0x1C6CB4, 7: 0x1C4C8C, 8: 0x143464, 9: 0xA8E4FF, 10: 0x0A1230,
    },
    14: {  # Empty / unavailable slot - muted slate (disabled state)
        2: 0x6C7686, 3: 0x646E7E, 4: 0x5C6676, 5: 0x4C5668,
        6: 0x3E4858, 7: 0x323A4A, 8: 0x262E3C, 9: 0x8A94A6, 10: 0x0A1230,
        13: 0x20283A, 14: 0x36405A,
    },
}


def build_palette_edits():
    """Return {member_index: {color_index: bgr555}} for every palette edit."""
    edits = {}

    main = {}
    for bank, ramp in ACTION_BANKS.items():
        for index, color in ramp.items():
            main[bank * 16 + index] = rgb(color)
    main.update(deck_palette(DEFAULT_DECK[0], DEFAULT_DECK[1], DECK_NORMAL))
    edits[PALETTE_MAIN] = main

    for terrain, speed, hue, sat in TERRAIN_DECKS:
        edits[terrain] = deck_palette(hue, sat, DECK_NORMAL)
        edits[speed] = deck_palette(hue, sat, DECK_SPEED, 1.1)
    return edits


# Default speed-up palette used when a background has no entry of its own.
# Member 267 is bank-0 entries 8..15 only, same layout as the terrain ones.
DEFAULT_SPEED_MEMBER = 267


def generate(members):
    members = list(members)
    edits = build_palette_edits()
    edits[DEFAULT_SPEED_MEMBER] = deck_palette(
        DEFAULT_DECK[0], DEFAULT_DECK[1], DECK_SPEED, 1.1
    )

    for member, updates in edits.items():
        raw = members[member]
        if raw[:4] != b"RLCN":
            raise SystemExit(f"member {member}: expected NCLR, found {raw[:4]!r}")
        if max(updates) >= len(nclr_colors(raw)):
            raise SystemExit(f"member {member}: palette too small for edit")
        members[member] = nclr_set_colors(raw, updates)
    return members


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="fail if the committed archive differs from generator output")
    parser.add_argument("--narc", type=Path, default=NARC_PATH)
    args = parser.parse_args()

    members, fnt = read_narc(args.narc)
    if len(members) != 342:
        raise SystemExit(f"unexpected member count {len(members)} (want 342)")

    out = write_narc(generate(members), fnt)
    current = args.narc.read_bytes()
    if args.check:
        if out != current:
            raise SystemExit("pl_batt_bg.narc is out of date; rerun generate_battle_command_ui.py")
        print("pl_batt_bg.narc matches generator output")
        return
    if out != current:
        args.narc.write_bytes(out)
        print("updated", args.narc)
    else:
        print("no changes")
    print("sha256", hashlib.sha256(out).hexdigest())


if __name__ == "__main__":
    main()
