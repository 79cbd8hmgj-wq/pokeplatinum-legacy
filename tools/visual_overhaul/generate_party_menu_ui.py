#!/usr/bin/env python3

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PALETTE_PATH = ROOT / "res" / "graphics" / "party_menu" / "shared.pal"

# Palette banks 0 and 1 drive the party-menu cursor/buttons/shared chrome.
# Keep all later banks untouched because they contain member/status/subscreen colors.
BANK_OVERRIDES = {
    0: [
        (98, 123, 123),   # transparent/key entry preserved
        (28, 45, 66),     # deep navy outline
        (248, 252, 255),   # cool white
        (41, 89, 184),     # royal blue shadow
        (47, 130, 230),    # clear blue
        (130, 199, 246),   # sky highlight
        (246, 172, 57),    # gold state accent
        (207, 220, 230),   # light slate
        (238, 103, 103),   # soft coral
        (184, 95, 105),    # coral shadow
        (121, 140, 158),   # slate
        (255, 190, 190),   # pale coral
        (188, 205, 218),   # cool panel
        (213, 225, 234),   # pale panel
        (255, 255, 255),   # white
        (246, 172, 57),    # gold focus
    ],
    1: [
        (98, 123, 123),   # transparent/key entry preserved
        (28, 45, 66),
        (248, 252, 255),
        (41, 89, 184),
        (47, 130, 230),
        (130, 199, 246),
        (246, 172, 57),
        (207, 220, 230),
        (238, 103, 103),
        (184, 95, 105),
        (121, 140, 158),
        (255, 190, 190),
        (188, 205, 218),
        (213, 225, 234),
        (255, 255, 255),
        (76, 174, 171),   # teal alternate-state focus
    ],
}


def load_palette() -> tuple[list[str], list[tuple[int, int, int]]]:
    lines = PALETTE_PATH.read_text().splitlines()
    if lines[:3] != ["JASC-PAL", "0100", "256"]:
        raise ValueError("Unexpected party-menu JASC palette header")
    colors = [tuple(map(int, line.split())) for line in lines[3:]]
    if len(colors) != 256:
        raise ValueError(f"Expected 256 colors, found {len(colors)}")
    return lines[:3], colors


def main() -> None:
    header, colors = load_palette()

    for bank, entries in BANK_OVERRIDES.items():
        if len(entries) != 16:
            raise ValueError(f"Bank {bank} must contain exactly 16 colors")
        start = bank * 16
        colors[start:start + 16] = entries

    out = header + [f"{r} {g} {b}" for r, g, b in colors]
    PALETTE_PATH.write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
