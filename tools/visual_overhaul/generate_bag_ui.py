#!/usr/bin/env python3

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BAG_DIR = ROOT / "res" / "graphics" / "bag"

# Opal MO1-1 palette contract. Only these entries may differ from the
# pre-G7.4 baseline. Keep NCGR pixels, NSCR mappings and pocket hitboxes intact.
MAIN_PALETTE_OVERRIDES = {
    1: (250, 246, 244),
    2: (240, 233, 236),
    3: (216, 202, 221),
    4: (132, 98, 135),
    5: (56, 53, 77),
    16: (238, 232, 241),
    18: (102, 91, 117),
    19: (216, 202, 221),
    20: (142, 165, 165),
    21: (194, 168, 123),
    22: (171, 146, 174),
    23: (238, 221, 192),
    24: (250, 246, 244),
    25: (216, 202, 221),
    27: (194, 168, 123),
    28: (216, 202, 221),
    29: (171, 146, 174),
    30: (132, 98, 135),
    31: (70, 65, 87),
    32: (240, 233, 236),
    33: (240, 233, 236),
    34: (240, 233, 236),
    35: (240, 233, 236),
    36: (240, 233, 236),
    37: (142, 165, 165),
    39: (216, 202, 221),
    41: (142, 165, 165),
    42: (115, 137, 151),
    43: (132, 98, 135),
    44: (171, 146, 174),
    45: (216, 202, 221),
    46: (142, 165, 165),
}

UI_ELEMENT_OVERRIDES = {
    0: (216, 202, 221),
    1: (246, 172, 57),
    2: (142, 165, 165),
    3: (132, 98, 135),
    4: (56, 53, 77),
}

BORDER_PALETTE_OVERRIDES = {
    1: (171, 146, 174),
    2: (194, 168, 123),
    3: (102, 91, 117),
    4: (238, 221, 192),
    6: (194, 168, 123),
    8: (132, 98, 135),
    9: (240, 233, 236),
    10: (171, 146, 174),
    14: (216, 202, 221),
    16: (142, 165, 165),
    18: (240, 233, 236),
    19: (70, 65, 87),
    20: (216, 202, 221),
    21: (240, 233, 236),
    22: (222, 214, 216),
    23: (171, 146, 174),
    24: (102, 91, 117),
    25: (132, 98, 135),
    26: (194, 168, 123),
    28: (102, 91, 117),
    29: (216, 202, 221),
    30: (171, 146, 174),
    31: (132, 98, 135),
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
    apply(BAG_DIR / "pokeball_borders.pal", BORDER_PALETTE_OVERRIDES)


if __name__ == "__main__":
    main()
