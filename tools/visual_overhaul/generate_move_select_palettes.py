#!/usr/bin/env python3
"""G7.1B move-slot palette generator.

Owner of the 19 per-type move-slot palettes in
``src/overlay011/move_palettes.c`` (``sMovePalette*``).  Each move slot on the
battle bottom screen loads one of these into BG palette bank 8+slot, so they
control the type-colored slot frame, the label plate and the structural
outline.

The script rewrites only the sixteen ``RGB()`` entries of each listed array
and is idempotent: output depends only on the (hue, saturation, value) specs
below, never on the current file contents.

Index contract (unchanged): 0 transparent key, 1 white, 2-9 light->dark ramp
(9 = pale highlight), 10 structural outline, 11 black, 12 neutral grey,
13 plate edge, 14 plate fill, 15 black.
"""

import argparse
import colorsys
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "overlay011" / "move_palettes.c"

# name -> (hue deg, saturation, value) of ramp entry 5, recorded from the
# retail tables so type identity is preserved.
TYPE_SPECS = {
    "sMovePaletteNormal": (262, 0.40, 0.65),
    "sMovePaletteFighting": (25, 1.00, 0.90),
    "sMovePaletteFlying": (218, 1.00, 0.90),
    "sMovePalettePoison": (287, 1.00, 0.90),
    "sMovePaletteGround": (34, 1.00, 0.77),
    "sMovePaletteRock": (35, 0.63, 0.52),
    "sMovePaletteBug": (49, 1.00, 0.71),
    "sMovePaletteGhost": (317, 0.50, 0.45),
    "sMovePaletteSteel": (240, 0.05, 0.61),
    "sMovePaletteMystery": (325, 0.39, 0.58),
    "sMovePaletteFire": (2, 0.93, 0.90),
    "sMovePaletteWater": (199, 1.00, 0.77),
    "sMovePaletteGrass": (103, 1.00, 0.71),
    "sMovePaletteElectric": (53, 1.00, 0.84),
    "sMovePalettePsychic": (324, 0.76, 0.94),
    "sMovePaletteIce": (203, 0.64, 0.90),
    "sMovePaletteDragon": (243, 0.64, 0.81),
    "sMovePaletteDark": (0, 0.17, 0.39),
    "sMovePaletteNone": (240, 0.10, 0.32),
}

KEY = (13, 14, 29)        # transparent key (unchanged)
OUTLINE = (1, 3, 7)       # deep navy structural outline
PLATE_EDGE = (17, 21, 26)  # cool slate lip under the label plate
PLATE_FILL = (29, 30, 31)  # cool pale-blue label plate


def q(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h / 360.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))
    return (round(r * 31), round(g * 31), round(b * 31))


def ramp(hue, sat, val):
    return [
        KEY,
        (31, 31, 31),
        q(hue, 0.18 * sat, 0.98),
        q(hue, 0.45 * sat, min(1.0, val + 0.18)),
        q(hue, 0.80 * sat, min(1.0, val + 0.08)),
        q(hue, sat, val),
        q(hue, sat + 0.04, val * 0.82),
        q(hue, sat + 0.06, val * 0.64),
        q(hue, sat + 0.08, val * 0.46),
        q(hue, 0.30 * sat, min(1.0, val + 0.22)),
        OUTLINE,
        (0, 0, 0),
        (12, 12, 12),
        PLATE_EDGE,
        PLATE_FILL,
        (0, 0, 0),
    ]


def render_array(name, entries):
    lines = ",\n".join(f"    RGB({r}, {g}, {b})" for r, g, b in entries)
    return f"ALIGN_4 static const u16 {name}[] = {{\n{lines}\n}};"


def generate(text):
    for name, (hue, sat, val) in TYPE_SPECS.items():
        pattern = re.compile(
            r"ALIGN_4 static const u16 " + name + r"\[\] = \{.*?\n\};", re.S
        )
        if not pattern.search(text):
            raise SystemExit(f"{name} not found in {SOURCE}")
        text = pattern.sub(lambda _m: render_array(name, ramp(hue, sat, val)), text, count=1)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    current = SOURCE.read_text()
    out = generate(current)
    if args.check:
        if out != current:
            sys.exit("move_palettes.c is out of date; rerun generate_move_select_palettes.py")
        print("move_palettes.c matches generator output")
        return
    if out != current:
        SOURCE.write_text(out)
        print("updated", SOURCE.relative_to(ROOT))
    else:
        print("no changes")


if __name__ == "__main__":
    main()
