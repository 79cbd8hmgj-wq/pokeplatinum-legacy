#!/usr/bin/env python3

from pathlib import Path
from PIL import Image, ImageDraw

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



def indexed_palette(filename: str) -> list[int]:
    source = Image.open(SUMMARY_DIR / filename)
    palette = source.getpalette()
    if palette is None:
        raise ValueError(f"{filename} is not an indexed PNG")
    return list(palette)


def make_tab_arrow() -> None:
    """Refresh the 8x16 tab arrow without changing its cell/animation contract."""
    image = Image.new("P", (8, 16), 0)
    image.putpalette(indexed_palette("tab_arrow.png"))
    pixels = image.load()

    # One compact left-facing chevron; the existing NCER horizontal flip
    # supplies the right-facing version and NANR supplies the bounce motion.
    for y in range(3, 13):
        distance = abs(7 - y)
        x_start = min(5, distance)
        for x in range(x_start, 7):
            pixels[x, y] = 2
    for y in range(5, 11):
        pixels[6, y] = 1

    image.save(SUMMARY_DIR / "tab_arrow.png")


def tile_linearize(source: Image.Image) -> Image.Image:
    """Convert a 64x32 half-frame into the 8x256 tile strip used by move_cursor.png."""
    if source.size != (64, 32):
        raise ValueError("move cursor half-frame must be 64x32")

    out = Image.new("P", (8, 256), 0)
    out.putpalette(source.getpalette())
    src = source.load()
    dst = out.load()

    tile_index = 0
    for tile_y in range(4):
        for tile_x in range(8):
            y_out = tile_index * 8
            for y in range(8):
                for x in range(8):
                    dst[x, y_out + y] = src[tile_x * 8 + x, tile_y * 8 + y]
            tile_index += 1

    return out


def make_move_cursor_half(outer: int, inner: int, palette: list[int]) -> Image.Image:
    """Create the left/open-center half used twice by the mirrored NCER cell."""
    image = Image.new("P", (64, 32), 0)
    image.putpalette(palette)
    draw = ImageDraw.Draw(image)

    # Thin cut-corner outer frame. The right edge stays open because the cell
    # mirrors this half around the centerline at runtime.
    draw.line([(4, 0), (63, 0)], fill=outer, width=2)
    draw.line([(1, 3), (1, 28)], fill=outer, width=2)
    draw.line([(4, 31), (63, 31)], fill=outer, width=2)
    draw.line([(1, 3), (4, 0)], fill=outer, width=2)
    draw.line([(1, 28), (4, 31)], fill=outer, width=2)

    draw.line([(5, 3), (63, 3)], fill=inner, width=1)
    draw.line([(4, 5), (4, 26)], fill=inner, width=1)
    draw.line([(5, 28), (63, 28)], fill=inner, width=1)

    return image


def make_move_cursor() -> None:
    """Rebuild both move-selection cursor states in the existing tile-strip format."""
    palette = indexed_palette("move_cursor.png")
    active = tile_linearize(make_move_cursor_half(3, 1, palette))
    alternate = tile_linearize(make_move_cursor_half(2, 1, palette))

    image = Image.new("P", (8, 512), 0)
    image.putpalette(palette)
    image.paste(active, (0, 0))
    image.paste(alternate, (0, 256))
    image.save(SUMMARY_DIR / "move_cursor.png")

def main() -> None:
    update_main_palette()
    update_sprite_palette()
    make_tab_arrow()
    make_move_cursor()


if __name__ == "__main__":
    main()
