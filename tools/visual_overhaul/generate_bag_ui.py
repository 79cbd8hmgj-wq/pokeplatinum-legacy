#!/usr/bin/env python3

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BAG_DIR = ROOT / "res" / "graphics" / "bag"

# Keep the bag layout, tilemaps, sprite geometry, and pocket-specific colors
# intact. This pass only modernizes the small shared chrome gradient.
MAIN_PALETTE_OVERRIDES = {
    1: (248, 252, 255),  # cool white
    2: (232, 241, 247),  # bright edge
    3: (188, 207, 220),  # light steel
    4: (130, 162, 190),  # medium steel-blue
    5: (62, 89, 112),    # deep rail
}

# ui_elements.pal is sparse; entries 2-4 are the existing blue UI accent
# ramp. Red/black and every unused entry remain untouched.
UI_ELEMENT_OVERRIDES = {
    2: (130, 199, 246),
    3: (47, 130, 230),
    4: (41, 89, 184),
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


def apply(path: Path, overrides: dict[int, tuple[int, int, int]]) -> None:
    header, colors = load_jasc(path)
    for index, rgb in overrides.items():
        colors[index] = rgb
    save_jasc(path, header, colors)


def main() -> None:
    apply(BAG_DIR / "bag_ui_main.pal", MAIN_PALETTE_OVERRIDES)
    apply(BAG_DIR / "ui_elements.pal", UI_ELEMENT_OVERRIDES)


if __name__ == "__main__":
    main()
