#!/usr/bin/env python3

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUMMARY_DIR = ROOT / "res" / "graphics" / "pokemon_summary_screen"

# The first ten 4bpp banks in tiles_main.pal are the main summary-page
# background/chrome banks. Their page-specific accent colors live in the
# upper entries of each bank. Only entries confirmed to be shared chrome are
# normalized across every bank.
MAIN_SHARED_CHROME = {
    1: (28, 45, 66),      # deep navy outline
    2: (164, 198, 228),   # cool blue edge
    3: (220, 233, 243),   # pale panel highlight
    5: (248, 252, 255),   # cool white
    15: (205, 217, 226),  # neutral panel separator
}

# Palette entry 6 is shared chrome in these banks only. Banks 7 and 8 use
# entry 6 for page-specific colors (black and pale yellow respectively), so
# touching it globally would corrupt those pages.
SECONDARY_OUTLINE_BANKS = (0, 1, 2, 3, 4, 5, 6, 9)
SECONDARY_OUTLINE = (82, 101, 119)

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
        for offset, rgb in MAIN_SHARED_CHROME.items():
            colors[base + offset] = rgb

    for bank in SECONDARY_OUTLINE_BANKS:
        colors[bank * 16 + 6] = SECONDARY_OUTLINE

    # Preserve the two page-specific entry-6 colors explicitly so rerunning
    # the generator repairs any earlier broad-palette pass.
    colors[7 * 16 + 6] = (0, 0, 0)
    colors[8 * 16 + 6] = (255, 255, 156)

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
