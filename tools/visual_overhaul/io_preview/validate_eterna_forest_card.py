#!/usr/bin/env python3
"""Static gates for the IO-PREVIEW Eterna Forest location card.

usage: validate_eterna_forest_card.py [--nitrogfx PATH] [--mockup OUT.png]

Source/asset checks only. This is NOT runtime or emulator validation.
With --nitrogfx, additionally converts the PNGs exactly like meson and checks the NCGR
tile stream equals the PNG's raster-of-tiles order (what the C blit loop assumes).
"""
import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
POP = ROOT / "res/graphics/map_popups"
SRC = (ROOT / "src/overlay005/map_name_popup.c").read_text()
HEADERS = (ROOT / "include/data/map_headers.h").read_text()
ORDER = (POP / "map_popup.order").read_text().split()
MESON = (POP / "meson.build").read_text()

VARIANTS = ["day", "dusk", "night"]
errors = []


def check(cond, msg):
    if not cond:
        errors.append(msg)
    print(("ok   " if cond else "FAIL ") + msg)


def define(name):
    m = re.search(rf"#define\s+{name}\s+(\d+)\b", SRC)
    return int(m.group(1)) if m else None


def fn_body(name):
    """Definition (not the forward declaration) of a function in map_name_popup.c."""
    m = re.search(rf"^[A-Za-z_ *]*\b{name}\([^;{{]*?\)\n\{{.*?\n\}}\n", SRC, re.S | re.M)
    if not m:
        raise SystemExit(f"definition of {name} not found")
    return m.group(0)


def tiles_of(img):
    w, h = img.size
    px = img.load()
    out = []
    for ty in range(h // 8):
        for tx in range(w // 8):
            out.append(bytes(px[tx * 8 + x, ty * 8 + y] for y in range(8) for x in range(8)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nitrogfx")
    ap.add_argument("--mockup")
    args = ap.parse_args()

    # --- geometry gate: card fits in the blank tiles of the existing popup window
    popup_w, popup_h = define("POPUP_WIDTH_TILES"), define("POPUP_HEIGHT_TILES")
    card_x, card_w = define("AREA_CARD_TILE_X"), define("AREA_CARD_WIDTH_TILES")
    win = re.search(r"Window_Add\(mapPopUp->bgConfig, &mapPopUp->window, BG_LAYER_MAIN_3, 0, 0, (\d+), (\d+),", SRC)
    win_w, win_h = int(win.group(1)), int(win.group(2))
    check(win_h == popup_h, f"window height {win_h} == popup height {popup_h} (card spans full window height)")
    check(card_x >= popup_w, f"card starts at tile {card_x}, after popup tiles 0-{popup_w - 1}")
    check(card_x + card_w <= win_w, f"card ends at tile {card_x + card_w - 1} within the {win_w}-tile window")
    n_tiles = card_w * popup_h

    # --- NARC member / meson / order gates
    base = ["city", "town", "route", "cave", "forest", "water", "park", "lake", "indoors"]
    expect_base = [f"{b}_popup.{e}" for b in base for e in ("NCGR", "NCLR")]
    check(ORDER[:18] == expect_base, "original 18 NARC members unchanged and in original order")
    check(ORDER[18:] == [f"card_eterna_forest_{v}.NCGR" for v in VARIANTS], "card NCGRs are NARC members 18-20, in order")
    for i, v in enumerate(VARIANTS):
        enum_name = f"AREA_CARD_NARC_ETERNA_FOREST_{v.upper()}"
        m = re.search(rf"{enum_name}(?:\s*=\s*(\d+))?", SRC)
        want = 18 + i
        got = int(m.group(1)) if (m and m.group(1)) else (18 + i if m else None)
        check(got == want, f"{enum_name} == {want}")
    check(f"'-num_tiles', '{n_tiles}'" in MESON, f"meson converts cards with -num_tiles {n_tiles}")
    check(all(f"'card_eterna_forest_{v}.png'" in MESON for v in VARIANTS), "meson lists all three card PNGs")
    check("map_popup_card_ncgrs" in MESON.split("custom_target")[1], "card NCGRs are inputs of the map_popup NARC")

    # --- style/map-header gates (popup gets header window ID minus one)
    enum_body = re.search(r"enum MapLabelWindowID \{(.*?)\};", HEADERS, re.S).group(1)
    names = [n.strip().split("=")[0].strip() for n in enum_body.split(",") if n.strip()]
    check(names.index("MAP_LABEL_WINDOW_FOREST") - 1 == define("POPUP_STYLE_FOREST"), "POPUP_STYLE_FOREST == FOREST window ID - 1")

    def header_block(name):
        return re.search(rf"\[{name}\] = \{{(.*?)\n    \}},", HEADERS, re.S).group(1)

    inside, outside = header_block("MAP_HEADER_ETERNA_FOREST"), header_block("MAP_HEADER_ETERNA_FOREST_OUTSIDE")
    check("MAP_LABEL_WINDOW_FOREST" in inside and "LocationNames_Text_EternaForest" in inside, "Eterna Forest header: forest style + EternaForest text (card eligible)")
    check("MAP_LABEL_WINDOW_ROUTE" in outside and "LocationNames_Text_EternaForest" in outside, "Eterna Forest outside header: route style (card gated off by style check)")

    # --- hook / lifecycle gates
    frame = fn_body("MapNamePopUp_DrawWindowFrame")
    check(frame.index("Window_BlitBitmapRect") < frame.index("MapNamePopUp_DrawAreaCard") < frame.index("Window_CopyToVRAM"),
          "card is drawn after the popup blit and before Window_CopyToVRAM (single hook)")
    check("Window_FillTilemap(&mapPopUp->window, 0)" in frame, "every redraw starts from Window_FillTilemap (clears any previous card)")
    card_fn = fn_body("MapNamePopUp_DrawAreaCard")
    check(card_fn.count("Graphics_GetCharData(NARC_INDEX_ARC__AREA_WIN_GRA") == 1, "card draw loads the resource exactly once")
    check("szByte >=" in card_fn, "card draw fails closed on a short resource")
    check("charData = NULL" in card_fn and re.search(r"tiles == NULL \|\| charData == NULL\)\s*\{\s*return;", card_fn) is not None
          and card_fn.index("tiles == NULL") < card_fn.index("charData->"),
          "card draw initialises charData and returns on a NULL load/unpack result before any dereference")
    check(card_fn.count("Heap_Free(tiles)") == 1 and card_fn.index("Heap_Free(tiles)") > card_fn.index("Window_BlitBitmapRect"),
          "non-NULL buffer is freed exactly once, after its last use (NULL path needs no free: GetCharacterData frees on unpack failure)")
    check("GetTimeOfDay()" in SRC and "TIMEOFDAY_TWILIGHT" in SRC and "TIMEOFDAY_LATE_NIGHT" in SRC, "time-of-day variant selected from the field lighting clock")
    for fn in ("MapNamePopUp_Hide", "MapNamePopUp_Destroy", "MapNamePopUp_Create"):
        body = fn_body(fn)
        check("AreaCard" not in body, f"{fn} unchanged by IO-PREVIEW (teardown path is vanilla)")

    # --- art gates
    forest = Image.open(POP / "forest_popup.png")
    pal16 = forest.getpalette()[:48]
    sheets = {}
    for v in VARIANTS:
        img = Image.open(POP / f"card_eterna_forest_{v}.png")
        check(img.mode == "P" and img.size == (card_w * 8, popup_h * 8), f"{v}: indexed {card_w * 8}x{popup_h * 8}")
        check(img.getpalette()[:48] == pal16, f"{v}: first 16 palette entries identical to forest_popup.png (shared palette slot 7)")
        used = set(img.tobytes())
        check(max(used) < 16, f"{v}: only palette indices 0-15 used")
        check(0 in used and len(used) > 6, f"{v}: transparent index 0 present, {len(used)} indices used")
        px = img.load()
        check(all(px[x, 0] == 0 and px[x, 1] == 0 for x in range(img.size[0])), f"{v}: top 2 rows transparent (clear of slide-in clip)")
        sheets[v] = img

    if args.nitrogfx:
        with tempfile.TemporaryDirectory() as td:
            for v, img in sheets.items():
                out = Path(td) / f"{v}.NCGR"
                subprocess.run([args.nitrogfx, str(POP / f"card_eterna_forest_{v}.png"), str(out),
                                "-version101", "-sopc", "-convertTo4Bpp", "-num_tiles", str(n_tiles)], check=True)
                data = out.read_bytes()
                rahc = data.index(b"RAHC")
                size = int.from_bytes(data[rahc + 0x18:rahc + 0x1C], "little")
                check(size == n_tiles * 32, f"{v}: NCGR tile data is {n_tiles} tiles ({size} bytes)")
                stream = [data[rahc + 0x20 + t * 32: rahc + 0x20 + t * 32 + 32] for t in range(n_tiles)]
                decoded = [bytes(b for byte in t for b in (byte & 15, byte >> 4)) for t in stream]
                check(decoded == tiles_of(img), f"{v}: NCGR tile stream == PNG raster-of-tiles order (matches the C blit loop)")
        if args.mockup:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import render_mockup
            render_mockup.render(args.nitrogfx, [None] + VARIANTS, args.mockup)
            print("wrote", args.mockup)

    if errors:
        print(f"\n{len(errors)} gate(s) FAILED")
        sys.exit(1)
    print("\nall static gates passed (source/asset level only; no runtime validation)")


if __name__ == "__main__":
    main()
