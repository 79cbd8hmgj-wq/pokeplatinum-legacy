#!/usr/bin/env python3

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUMMARY_DIR = ROOT / "res" / "graphics" / "pokemon_summary_screen"

# The first ten 4bpp banks in tiles_main.pal are the main summary-page
# background/chrome banks. Their page-specific accent colors live in the
# upper entries of each bank; only the repeated neutral/chrome entries below
# are normalized.
MAIN_CHROME = {
    1: (28, 45, 66),      # deep navy outline
    2: (164, 198, 228),   # cool blue edge
    3: (220, 233, 243),   # pale panel highlight
    5: (248, 252, 255),   # cool white
    6: (82, 101, 119),    # slate secondary outline
    15: (205, 217, 226),  # neutral panel separator
}

# Sprite palette banks 0-2 back the summary tabs/cursors/shared sprite chrome.
# Only the two repeated neutral entries are changed; page-specific colors,
# status colors, balls, ribbons, and icon palettes remain untouched.
SPRITE_CHROME = {
    1: (28, 45, 66),
    2: (248, 252, 255),
}


def load_jasc(path: Path) -> tuple[list[str], list[tuple[int, int, int]]]:
    lines = path.read_text().splitlines()
    if lines[:3] != ["JASC-PAL", "0100", "256"]:
        raise ValueError(f"Unexpected JASC palette header in {path}")
    colors = [tuple(map(int, line.split())) for line in lines[3:]]
    if len(colors) != 256:
        raise ValueError(f"Expected 256 colors in {path}, found {len(colors)}")
    return lines[:3], colors


def save_jasc(path: Path, header: list[str], colors: list[tuple[int, int, int]]) -> None:
    path.write_text("\n".join(header + [f"{r} {g} {b}" for r, g, b in colors]) + "\n")


def update_main_palette() -> None:
    path = SUMMARY_DIR / "tiles_main.pal"
    header, colors = load_jasc(path)

    for bank in range(10):
        base = bank * 16
        for offset, rgb in MAIN_CHROME.items():
            colors[base + offset] = rgb

    save_jasc(path, header, colors)


def update_sprite_palette() -> None:
    path = SUMMARY_DIR / "sprites.pal"
    header, colors = load_jasc(path)

    for bank in range(3):
        base = bank * 16
        for offset, rgb in SPRITE_CHROME.items():
            colors[base + offset] = rgb

    save_jasc(path, header, colors)


def main() -> None:
    update_main_palette()
    update_sprite_palette()


if __name__ == "__main__":
    main()
