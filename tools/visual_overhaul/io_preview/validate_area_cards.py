#!/usr/bin/env python3
"""Static gates for the IO-PREVIEW area cards (Eterna Forest pilot + Sinnoh expansion).

usage: validate_area_cards.py [--nitrogfx PATH] [--mockup OUT.png]

Source/asset checks only. This is NOT runtime or emulator validation.
The card table (sAreaCards) in src/overlay005/map_name_popup.c is the single source of truth: every
gate is derived from it and cross-checked against include/data/map_headers.h, map_popup.order,
meson.build and the PNGs. With --nitrogfx, additionally converts every PNG exactly like meson and
checks the NCGR tile stream equals the PNG's raster-of-tiles order (what the C blit loop assumes).
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
BASE_STYLES = ["city", "town", "route", "cave", "forest", "water", "park", "lake", "indoors"]
BUILDING_MAP_TYPES = {"MAP_TYPE_INDOORS", "MAP_TYPE_POKECENTER"}  # MapHeader_IsBuilding
FIRST_CARD_MEMBER = 18
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
    return [bytes(px[tx * 8 + x, ty * 8 + y] for y in range(8) for x in range(8))
            for ty in range(h // 8) for tx in range(w // 8)]


def parse_members():
    body = re.search(r"enum AreaCardNarcMember \{(.*?)\};", SRC, re.S).group(1)
    members, value = {}, None
    for item in (i.strip() for i in body.split(",") if i.strip()):
        name, _, num = (p.strip() for p in item.partition("="))
        value = int(num) if num else value + 1
        members[name] = value
    return members


def parse_cards(members):
    body = re.search(r"sAreaCards\[\] = \{(.*?)\n\};", SRC, re.S).group(1)
    cards = []
    for m in re.finditer(r"\{\s*LocationNames_Text_(\w+),\s*(POPUP_STYLE_\w+),\s*(AREA_CARD_NARC_\w+),\s*(TRUE|FALSE)\s*\}", body):
        text, style, member, tod = m.groups()
        cards.append({"text": text, "style_const": style, "style": define(style), "member": members[member],
                      "member_name": member, "tod": tod == "TRUE"})
    return cards


def card_files(card):
    """NARC member indices -> order-file stems for one card (1 or 3 members)."""
    n = 3 if card["tod"] else 1
    return [ORDER[card["member"] + i] for i in range(n)]


def headers_for(text):
    out = []
    for name, block in re.findall(r"\[(MAP_HEADER_\w+)\] = \{(.*?)\n    \},", HEADERS, re.S):
        if re.search(rf"mapLabelTextID = LocationNames_Text_{text}\b", block):
            style = re.search(r"mapLabelWindowID = (MAP_LABEL_WINDOW_\w+)", block).group(1)
            mtype = re.search(r"mapType = (\w+)", block).group(1)
            out.append((name, style, mtype))
    return out


MEMBERS = parse_members()
CARDS = parse_cards(MEMBERS)


def mockup_rows():
    """(style name, card PNG stem or None): one sign-only row per style used, then every card."""
    rows, seen = [], []
    for c in CARDS:
        st = BASE_STYLES[c["style"]]
        if st not in seen:
            seen.append(st)
    rows += [(s, None) for s in seen]
    for c in CARDS:
        for stem in card_files(c):
            rows.append((BASE_STYLES[c["style"]], stem.replace(".NCGR", "")))
    return rows


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

    # --- card table gates
    check(len(CARDS) >= 6, f"card table parsed: {len(CARDS)} locations")
    keys = [(c["text"], c["style"]) for c in CARDS]
    check(len(set(keys)) == len(keys), "card table has no duplicate (location name, popup style) key")
    expected_members = []
    for c in CARDS:
        expected_members += range(c["member"], c["member"] + (3 if c["tod"] else 1))
    check(list(MEMBERS.values()) == list(range(FIRST_CARD_MEMBER, FIRST_CARD_MEMBER + len(MEMBERS))),
          f"AreaCardNarcMember is contiguous from {FIRST_CARD_MEMBER}")
    check(expected_members == list(MEMBERS.values()), "every enum member is owned by exactly one table entry, in order")
    check(len(ORDER) == FIRST_CARD_MEMBER + len(MEMBERS), f"map_popup.order has {len(ORDER)} entries = 18 popup + {len(MEMBERS)} card members")

    # --- NARC order / meson gates
    expect_base = [f"{b}_popup.{e}" for b in BASE_STYLES for e in ("NCGR", "NCLR")]
    check(ORDER[:18] == expect_base, "original 18 NARC members unchanged and in original order")
    check(all(o.startswith("card_") and o.endswith(".NCGR") for o in ORDER[18:]), "members 18+ are card NCGRs")
    check(len(set(ORDER)) == len(ORDER), "no duplicate NARC member names")
    check(f"'-num_tiles', '{n_tiles}'" in MESON, f"meson converts cards with -num_tiles {n_tiles}")
    meson_cards = re.search(r"map_popup_card_files = files\((.*?)\)", MESON, re.S).group(1)
    listed = re.findall(r"'(card_\w+)\.png'", meson_cards)
    check(sorted(listed) == sorted(o[:-5] for o in ORDER[18:]), "meson lists exactly the PNGs behind NARC members 18+")
    check("map_popup_card_ncgrs" in MESON.split("custom_target")[1], "card NCGRs are inputs of the map_popup NARC")

    # --- style / map-header gates (popup gets header window ID minus one)
    enum_body = re.search(r"enum MapLabelWindowID \{(.*?)\};", HEADERS, re.S).group(1)
    names = [n.strip().split("=")[0].strip() for n in enum_body.split(",") if n.strip()]
    for style_const in sorted({c["style_const"] for c in CARDS}):
        label = "MAP_LABEL_WINDOW_" + style_const.removeprefix("POPUP_STYLE_")
        check(names.index(label) - 1 == define(style_const), f"{style_const} == {label} - 1")

    for c in CARDS:
        text, label = c["text"], f"MAP_LABEL_WINDOW_{BASE_STYLES[c['style']].upper()}"
        hs = headers_for(text)
        eligible = [h for h in hs if h[1] == label]
        reachable = [h for h in eligible if h[2] not in BUILDING_MAP_TYPES]
        gated_out = [h for h in hs if h[1] != label]
        check(len(reachable) > 0, f"{text}: {len(reachable)} header(s) show the popup with style {label} (card reachable)")
        indoor = [h[0] for h in eligible if h[2] in BUILDING_MAP_TYPES]
        print(f"     {text}: eligible headers: {', '.join(h[0] for h in reachable)}")
        if indoor:
            print(f"     {text}: same name+style but indoors (no popup, so no card): {', '.join(indoor)}")
        if gated_out:
            print(f"     {text}: same name, other style (gated off by the style check): {', '.join(h[0] + '/' + h[1] for h in gated_out)}")

        files = card_files(c)
        stem = files[0][: -len(".NCGR")]
        if c["tod"]:
            exp = [f"{stem[: -len('_day')]}_{v}.NCGR" for v in VARIANTS] if stem.endswith("_day") else None
            check(exp == files, f"{text}: members {c['member']}-{c['member'] + 2} are the day/dusk/night triple {files}")
        else:
            check(len(files) == 1 and not re.search(r"_(day|dusk|night)\.NCGR$", files[0]), f"{text}: single time-independent member {files}")

    # --- hook / lifecycle gates
    frame = fn_body("MapNamePopUp_DrawWindowFrame")
    check(frame.index("Window_BlitBitmapRect") < frame.index("MapNamePopUp_DrawAreaCard") < frame.index("Window_CopyToVRAM"),
          "card is drawn after the popup blit and before Window_CopyToVRAM (single hook)")
    check("Window_FillTilemap(&mapPopUp->window, 0)" in frame, "every redraw starts from Window_FillTilemap (clears any previous card)")
    check(frame.count("MapNamePopUp_DrawAreaCard") == 1, "exactly one DrawAreaCard call site")
    card_fn = fn_body("MapNamePopUp_DrawAreaCard")
    check(card_fn.count("Graphics_GetCharData(NARC_INDEX_ARC__AREA_WIN_GRA") == 1, "card draw loads the resource exactly once")
    check("szByte >=" in card_fn, "card draw fails closed on a short resource")
    check("charData = NULL" in card_fn and re.search(r"tiles == NULL \|\| charData == NULL\)\s*\{\s*return;", card_fn) is not None
          and card_fn.index("tiles == NULL") < card_fn.index("charData->"),
          "card draw initialises charData and returns on a NULL load/unpack result before any dereference")
    check(card_fn.count("Heap_Free(tiles)") == 1 and card_fn.index("Heap_Free(tiles)") > card_fn.index("Window_BlitBitmapRect"),
          "non-NULL buffer is freed exactly once, after its last use (NULL path needs no free: GetCharacterData frees on unpack failure)")
    sel = fn_body("MapNamePopUp_GetAreaCardMember")
    check("entryID != card->textID" in sel and "windowID != card->popupStyle" in sel, "eligibility requires both location name and popup style")
    check("NELEMS(sAreaCards)" in sel, "selection loop is bounded by the table size")
    check("hasTimeOfDayVariants" in sel, "time-of-day offset is applied only to cards with variants")
    var = fn_body("MapNamePopUp_GetAreaCardVariant")
    check("GetTimeOfDay()" in var and "TIMEOFDAY_TWILIGHT" in var and "TIMEOFDAY_LATE_NIGHT" in var and "TIMEOFDAY_NIGHT" in var,
          "time-of-day variant selected from the field lighting clock (twilight=dusk; night/late night=night)")
    enum_v = re.search(r"enum AreaCardTimeOfDayVariant \{(.*?)\};", SRC, re.S).group(1)
    check([x.strip() for x in enum_v.split(",") if x.strip()] == ["AREA_CARD_VARIANT_DAY", "AREA_CARD_VARIANT_DUSK", "AREA_CARD_VARIANT_NIGHT"],
          "variant enum order is day, dusk, night (matches the consecutive NARC triples)")
    for fn in ("MapNamePopUp_Hide", "MapNamePopUp_Destroy", "MapNamePopUp_Create", "MapNamePopUp_Show", "FieldSystem_RequestLocationName"):
        body = fn_body(fn)
        check("AreaCard" not in body, f"{fn} unchanged by IO-PREVIEW (show/teardown paths are vanilla)")

    # --- art gates: each PNG against the palette of its own popup style
    sheets = {}
    for c in CARDS:
        style = BASE_STYLES[c["style"]]
        pal16 = Image.open(POP / f"{style}_popup.png").getpalette()[:48]
        for f in card_files(c):
            stem = f[: -len(".NCGR")]
            path = POP / f"{stem}.png"
            check(path.exists(), f"{stem}: PNG exists")
            img = Image.open(path)
            check(img.mode == "P" and img.size == (card_w * 8, popup_h * 8), f"{stem}: indexed {card_w * 8}x{popup_h * 8}")
            check(img.getpalette()[:48] == pal16, f"{stem}: first 16 palette entries identical to {style}_popup.png (shared palette slot 7)")
            used = set(img.tobytes())
            check(max(used) < 16, f"{stem}: only palette indices 0-15 used")
            # >= 5 only rejects flat/degenerate art: the cave and lake palettes have a single true dark, so
            # their night scenes are inherently limited (see the IO-PREVIEW docs).
            check(0 in used and len(used) >= 5, f"{stem}: transparent index 0 present, {len(used)} indices used")
            px = img.load()
            check(all(px[x, 0] == 0 and px[x, 1] == 0 for x in range(img.size[0])), f"{stem}: top 2 rows transparent (clear of slide-in clip)")
            sheets[stem] = img

    if args.nitrogfx:
        with tempfile.TemporaryDirectory() as td:
            for stem, img in sheets.items():
                out = Path(td) / f"{stem}.NCGR"
                subprocess.run([args.nitrogfx, str(POP / f"{stem}.png"), str(out),
                                "-version101", "-sopc", "-convertTo4Bpp", "-num_tiles", str(n_tiles)], check=True)
                data = out.read_bytes()
                rahc = data.index(b"RAHC")
                size = int.from_bytes(data[rahc + 0x18:rahc + 0x1C], "little")
                check(size == n_tiles * 32, f"{stem}: NCGR tile data is {n_tiles} tiles ({size} bytes)")
                stream = [data[rahc + 0x20 + t * 32: rahc + 0x20 + t * 32 + 32] for t in range(n_tiles)]
                decoded = [bytes(b for byte in t for b in (byte & 15, byte >> 4)) for t in stream]
                check(decoded == tiles_of(img), f"{stem}: NCGR tile stream == PNG raster-of-tiles order (matches the C blit loop)")
        if args.mockup:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import render_mockup
            render_mockup.render(args.nitrogfx, mockup_rows(), args.mockup)
            print("wrote", args.mockup)

    if errors:
        print(f"\n{len(errors)} gate(s) FAILED")
        sys.exit(1)
    print("\nall static gates passed (source/asset level only; no runtime validation)")


if __name__ == "__main__":
    main()
