#!/usr/bin/env python3
"""Validate the G7.5 global window pass (standard frames, scroll cursor, wait dial)."""

import hashlib
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import generate_ui_foundation as gen  # noqa: E402

WINDOWS = ROOT / "res" / "graphics" / "windows"

# Decorative frames 6-20 are player choices and must stay byte-identical
# (pixel indices + palette).
DECORATIVE_DIGESTS = {
    "message_box_05.png": "b01b742a82f7b1201ea14cedddfcfffdda6c5123bf994011210def42488c7c9c",
    "message_box_06.png": "b08e0c902549405faeba250d1f94f62ca23ed7c28ba798711605392795311505",
    "message_box_07.png": "4b4440f31b3ac9e7ccfd857e5aea2ed43d1e0257710c13336cff0abeaf559340",
    "message_box_08.png": "678281704d639bb8f6c5623163000be001d7b850b341880007333d0eaddd1d85",
    "message_box_09.png": "e1109645b706c283025029f200afd53b9809384245d70292130845c9972c9ac8",
    "message_box_10.png": "fe490e6730cba202005fe911e8e1d5deb33dee73ab1eb005c6aa77a295239f63",
    "message_box_11.png": "70aa43ba07c606ff700f6861f9611bbc9275396ff88b0a6781d7237c27b3983f",
    "message_box_12.png": "77aaa958be5035ea0bec8b890d0329c6420dea5b8114b6cf5caebf18d521a2f7",
    "message_box_13.png": "b81b0cf5420331f93dcbd61bd1e5e7dd0d45c6625f0691a59cf00d5ef4479705",
    "message_box_14.png": "15b12597a43a9921f9bec4496e57b04cfac4c8f65cedf1aa8938b5d38bd0db45",
    "message_box_15.png": "fc52636da7acfd20344569ac3542d83046839fa5be4aa7df499e17c08c835cc1",
    "message_box_16.png": "3ecdd163362bf4d1f426f702749dc8bc3c65bd04d51c6138334462de6ce3285b",
    "message_box_17.png": "34abf997c506a3afc2edec39545682e17a250fa09a64bd6bd9ce54e87bb415f5",
    "message_box_18.png": "70bebd1a4360083fb7714eb1ecb8ea18767e7f03ff6072bda934cc18ae650d96",
    "message_box_19.png": "b7eabb71785b68b489212b1c1bd1fd0a137b018e399891ea3cae91a51e3fa379",
}
ALL_FRAMES = [f"message_box_{i:02d}.png" for i in range(20)]
failures = []


def check(condition, message):
    if not condition:
        failures.append(message)


def lum(rgb):
    def chan(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b)


def contrast(a, b):
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def cursor_cells(image):
    """Return {frame: {(bar_x, y): index}} as DrawMessageBoxScrollCursor blits them."""
    px = image.load()
    frames = {}
    for frame in range(3):
        cells = {}
        for cell_y in range(16):
            for cell_x in range(gen.CURSOR_SRC_X, 16):
                tile = frame * 4 + (cell_y // 8) * 2 + (cell_x // 8)
                value = px[tile * 8 + cell_x % 8, cell_y % 8]
                if value:
                    cells[(cell_x - gen.CURSOR_SRC_X + 1, cell_y)] = value
        frames[frame] = cells
    return frames


def main():
    # --- standard system / field frames: contract + cool G7 palette ---------
    for name in ("standard_system.png", "standard_field.png"):
        image = Image.open(WINDOWS / name)
        check(image.size == (24, 24) and image.mode == "P", f"{name}: size/mode changed")
        pal = image.getpalette()
        for index, rgb in gen.PALETTE_OVERRIDES.items():
            check(tuple(pal[index * 3:index * 3 + 3]) == rgb, f"{name}: palette entry {index} drifted")
    system = Image.open(WINDOWS / "standard_system.png").getpalette()
    for index in (2, 3, 4, 6, 7, 8):
        r, g, b = system[index * 3:index * 3 + 3]
        check(b >= r and b >= g - 20, f"standard palette entry {index} is not cool")
    fill, outline = tuple(system[3:6]), tuple(system[12:15])
    check(lum(fill) > 0.9, "system fill not light")
    check(contrast(outline, fill) >= 10, "system outline/fill contrast low")

    # --- scroll cursor ------------------------------------------------------
    cursor = Image.open(WINDOWS / "scroll_cursor.png")
    check(cursor.size == (96, 8) and cursor.mode == "P", "scroll_cursor: size/mode changed (12 tiles = 3 frames x 2x2)")
    frames = cursor_cells(cursor)
    shapes = set()
    for frame, cells in frames.items():
        xs = [x for x, _ in cells]
        ys = [y for _, y in cells]
        check(cells, f"scroll cursor frame {frame} empty")
        check(min(xs) >= 1 and max(xs) <= 9, f"scroll cursor frame {frame} leaves the 1-9 bar cols: {min(xs)}..{max(xs)}")
        check(max(ys) <= 15, f"scroll cursor frame {frame} clipped")
        expected_cursor_indices = {gen.FRAME_LIGHT, gen.FRAME_DARK}
        check(
            set(cells.values()) == expected_cursor_indices,
            f"scroll cursor frame {frame} must use both frame-polarity indices {expected_cursor_indices}",
        )
        top = min(ys)
        shapes.add(frozenset((x, y - top, v) for (x, y), v in cells.items()))
    check(len(shapes) == 1, "scroll cursor frames must be the same art (bounce only)")
    tops = [min(y for _, y in frames[f]) for f in range(3)]
    check(tops[0] < tops[1] < tops[2], f"scroll cursor must bounce downward over 3 frames: {tops}")
    # bytes beyond the 12 tiles are not allowed
    check(cursor.size[0] // 8 == 12, "scroll cursor tile count changed")

    # --- wait dial ----------------------------------------------------------
    dial = Image.open(WINDOWS / "wait_dial.png")
    check(dial.size == (16, 128) and dial.mode == "P", "wait_dial: size/mode changed (8 frames of 16x16)")
    px = dial.load()
    for frame in range(8):
        for point_index, (x, y) in enumerate(gen.DIAL_POINTS):
            if point_index == frame:
                pattern = gen.DIAL_HEAD_PATTERN
            elif point_index == (frame - 1) % 8:
                pattern = gen.DIAL_TRAIL_PATTERN
            else:
                pattern = gen.DIAL_REST_PATTERN

            expected = {(x + dx, y + dy): value for dx, dy, value in pattern}
            for yy in range(y, y + 2):
                for xx in range(x, x + 2):
                    actual = px[xx, frame * 16 + yy]
                    check(
                        actual == expected.get((xx, yy), 0),
                        f"wait dial frame {frame} point {point_index}: unexpected pixel at {xx},{yy}",
                    )
                    if actual:
                        check(xx <= 9, f"wait dial frame {frame} paints col {xx} (>9) over the frame outline")

    # --- all selectable frames: polarity pair stays readable on the bar -----
    for name in ALL_FRAMES:
        image = Image.open(WINDOWS / name)
        pal = image.getpalette()
        entry = lambda i: tuple(pal[i * 3:i * 3 + 3])  # noqa: E731
        bar = entry(image.getpixel((32, 8)))  # frame tile +10: solid bar colour
        light_contrast = contrast(entry(gen.FRAME_LIGHT), bar)
        dark_contrast = contrast(entry(gen.FRAME_DARK), bar)
        best_contrast = max(light_contrast, dark_contrast)
        check(
            best_contrast >= 4.5,
            f"{name}: cursor/dial polarity pair too faint on bar {bar} "
            f"(entry {gen.FRAME_LIGHT}={light_contrast:.2f}, "
            f"entry {gen.FRAME_DARK}={dark_contrast:.2f})",
        )

    # --- decorative frames untouched ----------------------------------------
    for name, digest in DECORATIVE_DIGESTS.items():
        image = Image.open(WINDOWS / name)
        actual = hashlib.sha256(image.tobytes() + bytes(image.getpalette())).hexdigest()
        check(actual == digest, f"{name}: decorative frame changed")

    if failures:
        print("G7.5 validation FAILED")
        for failure in failures:
            print(" -", failure)
        return 1
    print("G7.5 global windows validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
