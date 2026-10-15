#!/usr/bin/env python3
"""Guard Pokédex LCD/background memory ownership before the V3 layout pass.

Static source contract only; actual compositing and touch fidelity need emulator QA.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
graphics = (ROOT / "src/applications/pokedex/pokedex_graphics.c").read_text()
main = (ROOT / "src/applications/pokedex/pokedex_main.c").read_text()
meson = (ROOT / "res/graphics/pokedex/meson.build").read_text()

layers = {
    "MAIN_1": ("0", "16", "BG_TYPE_STATIC"),
    "MAIN_2": ("1", "16", "BG_TYPE_STATIC"),
    "MAIN_3": ("3", "16", "BG_TYPE_STATIC"),
    "SUB_1": ("0", "16", "BG_TYPE_STATIC"),
    "SUB_2": ("2", "16", "BG_TYPE_STATIC"),
    "SUB_3": ("1", "256", "BG_TYPE_AFFINE"),
}
for layer, (priority, depth, bg_type) in layers.items():
    pattern = (
        r"BgTemplate\s+(\w+)\s*=\s*\{"
        r"(?P<body>.*?)\};\s*Bg_InitFromTemplate"
        r"\(bgConfig,\s*BG_LAYER_" + layer + r",\s*&\1,\s*" + bg_type + r"\)"
    )
    matches = re.findall(pattern, graphics, re.S)
    assert len(matches) == 1, f"Expected unique template for {layer}"
    body = matches[0][1]
    assert re.search(r"\.priority\s*=\s*" + priority + r"\b", body), layer
    mode = "GX_BG_COLORMODE_" + depth
    assert re.search(r"\.colorMode\s*=\s*" + mode + r"\b", body), layer

assert "Bg_SetPriority(BG_LAYER_MAIN_0, 2)" in graphics
assert "EnableTouchPad();" in main and "InitializeTouchPad(4)" in main
assert "NARC_INDEX_RESOURCE__ENG__ZUKAN__ZUKAN" in graphics
for path in (
    "scroll_main_background.png", "scroll_sub_background.png",
    "scroll_main_background.NSCR", "scroll_sub.NSCR",
    "scroll_wheel.png", "scroll_wheel.NSCR",
    "search_main.NSCR", "info_main.NSCR", "area_map.NSCR",
):
    assert "'" + path + "'" in meson, path
print("PASS: Pokédex dual-LCD BG layer and asset build contracts")
