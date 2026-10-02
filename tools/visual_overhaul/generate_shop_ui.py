#!/usr/bin/env python3

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHOP_DIR = ROOT / "res" / "graphics" / "shop_menu"

# default.pal and frontier.pal share the same neutral/chrome entries 0-8.
# Their distinct shop/frontier accent colors live at 9-15 and are preserved.
SHARED_CHROME = {
    1: (248, 252, 255),
    2: (205, 217, 226),
    4: (82, 101, 119),
    5: (232, 241, 247),
    6: (188, 207, 220),
    7: (130, 162, 190),
    8: (62, 89, 112),
}

# The shop cursor/arrow palette uses the same sparse blue ramp layout as the
# bag UI. Keep red, black, and all unused entries unchanged.
SPRITE_OVERRIDES = {
    2: (130, 199, 246),
    3: (47, 130, 230),
    4: (41, 89, 184),
}


def load_jasc(path: Path, expected_count: int) -> tuple[list[str], list[tuple[int, int, int]]]:
    lines = path.read_text().splitlines()
    if lines[:2] != ["JASC-PAL", "0100"]:
        raise ValueError(f"Unexpected JASC palette header in {path}")
    if int(lines[2]) != expected_count:
        raise ValueError(f"Expected {expected_count} colors in {path}, header says {lines[2]}")
    colors = [tuple(map(int, line.split())) for line in lines[3:]]
    if len(colors) != expected_count:
        raise ValueError(f"Expected {expected_count} colors in {path}, found {len(colors)}")
    return lines[:3], colors


def save_jasc(path: Path, header: list[str], colors: list[tuple[int, int, int]]) -> None:
    path.write_text("\n".join(header + [f"{r} {g} {b}" for r, g, b in colors]) + "\n")


def apply(path: Path, expected_count: int, overrides: dict[int, tuple[int, int, int]]) -> None:
    header, colors = load_jasc(path, expected_count)
    for index, rgb in overrides.items():
        colors[index] = rgb
    save_jasc(path, header, colors)


def main() -> None:
    apply(SHOP_DIR / "default.pal", 16, SHARED_CHROME)
    apply(SHOP_DIR / "frontier.pal", 16, SHARED_CHROME)
    apply(SHOP_DIR / "sprites.pal", 256, SPRITE_OVERRIDES)


if __name__ == "__main__":
    main()
