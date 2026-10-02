#!/usr/bin/env python3
"""Generate the first G5 battle-terrain palette refresh.

This pass deliberately changes only JASC-PAL source files. Sprite geometry,
NCGR pixels, cells, animations, archive ordering, and battle logic remain
unchanged.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TERRAIN = ROOT / "res" / "graphics" / "battle" / "terrain"

PALETTES = {
    "grass/day.pal": [
        (184, 216, 255), (68, 61, 42), (0, 0, 0), (0, 0, 0),
        (0, 0, 0), (0, 0, 0), (188, 224, 103), (126, 211, 143),
        (91, 194, 121), (62, 174, 98), (42, 148, 77), (23, 113, 58),
        (0, 0, 0), (231, 195, 94), (184, 142, 61), (122, 88, 42),
    ],
    "grass/evening.pal": [
        (221, 166, 201), (91, 55, 42), (38, 15, 31), (38, 15, 31),
        (38, 15, 31), (38, 15, 31), (201, 172, 83), (144, 174, 111),
        (112, 158, 92), (85, 140, 76), (65, 120, 62), (45, 96, 48),
        (38, 15, 31), (240, 157, 76), (198, 116, 50), (140, 77, 39),
    ],
    "grass/night.pal": [
        (90, 127, 209), (34, 45, 68), (3, 8, 27), (3, 8, 27),
        (3, 8, 27), (3, 8, 27), (76, 125, 107), (57, 137, 151),
        (43, 124, 136), (32, 109, 116), (23, 92, 94), (14, 72, 72),
        (3, 8, 27), (111, 118, 133), (84, 91, 107), (58, 65, 82),
    ],
    "cave/all.pal": [
        (238, 244, 255), (67, 64, 82), (0, 0, 0), (0, 0, 0),
        (0, 0, 0), (0, 0, 0), (0, 0, 0), (93, 91, 151),
        (85, 99, 153), (73, 86, 143), (65, 75, 119), (60, 66, 97),
        (54, 58, 79), (43, 48, 68), (31, 39, 58), (13, 25, 43),
    ],
    "ice/day.pal": [
        (184, 205, 255), (105, 91, 147), (0, 0, 0), (0, 0, 0),
        (0, 0, 0), (0, 0, 0), (169, 196, 255), (169, 211, 255),
        (178, 222, 255), (199, 235, 255), (220, 244, 255), (239, 250, 255),
        (255, 255, 255), (204, 208, 232), (145, 145, 184), (88, 79, 137),
    ],
    "distortion_world/all.pal": [
        (247, 243, 255), (0, 0, 0), (0, 0, 0), (0, 0, 0),
        (0, 0, 0), (0, 0, 0), (187, 126, 187), (199, 137, 204),
        (211, 148, 218), (190, 128, 199), (166, 107, 177), (143, 91, 156),
        (119, 75, 134), (94, 59, 111), (72, 45, 88), (48, 31, 62),
    ],
}


def write_jasc(path: Path, colors: list[tuple[int, int, int]]) -> None:
    if len(colors) != 16:
        raise ValueError(f"{path}: expected exactly 16 colors")
    body = ["JASC-PAL", "0100", "16"]
    body.extend(f"{r} {g} {b}" for r, g, b in colors)
    path.write_text("\n".join(body) + "\n", encoding="ascii")


def main() -> None:
    for relative, colors in PALETTES.items():
        write_jasc(TERRAIN / relative, colors)


if __name__ == "__main__":
    main()
