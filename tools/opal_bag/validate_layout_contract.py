#!/usr/bin/env python3
"""Check MO1 decorative panel geometry against the real Bag window/touch contract.

This is a source-structure guard, not runtime proof. Do not infer that the
two-screen V3 concept's proposed layout is implemented by background changes.
"""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[2]
MAIN=(ROOT/"src/applications/bag/main.c").read_text()
WIN=(ROOT/"src/applications/bag/windows.c").read_text()
SPR=(ROOT/"src/applications/bag/sprites.c").read_text()
ART=(ROOT/"tools/opal_bag/generate_installed_bag_art.py").read_text()
assert "#define BAG_UI_NUM_VISIBLE_ITEMS 9" in (ROOT/"include/applications/bag/defs.h").read_text()
assert ".maxDisplay = BAG_UI_NUM_VISIBLE_ITEMS" in MAIN
assert ".lineSpacing = 16" in MAIN
assert "template.textXOffset = OPAL_LIST_TEXT_INSET;" in MAIN
assert "template.textXOffset = 35 + OPAL_LIST_TEXT_INSET;" in MAIN
assert "#define OPAL_ITEM_LIST_TILE_X          14" in WIN
assert "#define OPAL_DESCRIPTION_TILE_Y        18" in WIN
assert "#define OPAL_DESCRIPTION_TEXT_X        44" in WIN
assert "Window_Add(controller->bgConfig, &controller->windows[BAG_UI_WINDOW_ITEM_LIST], BG_LAYER_MAIN_2, OPAL_ITEM_LIST_TILE_X, OPAL_ITEM_LIST_TILE_Y, ITEM_LIST_WINDOW_WIDTH, ITEM_LIST_WINDOW_HEIGHT" in WIN
assert "Window_Add(controller->bgConfig, &controller->windows[BAG_UI_WINDOW_ITEM_DESCRIPTION], BG_LAYER_MAIN_0, OPAL_DESCRIPTION_TILE_X, OPAL_DESCRIPTION_TILE_Y, ITEM_DESCRIPTION_WINDOW_WIDTH, ITEM_DESCRIPTION_WINDOW_HEIGHT" in WIN
for name, value in (("OPAL_ITEM_HIGHLIGHT_X", 177), ("OPAL_ITEM_HIGHLIGHT_Y", 24), ("OPAL_ITEM_HIGHLIGHT_ROW_PITCH", 16)):
    match = re.search(r"^#define\\s+" + name + r"\\s+(\\d+)\\s*$", SPR, re.MULTILINE)
    assert match is not None and int(match.group(1)) == value, f"{name}: expected {value}"
assert "ManagedSprite_SetPositionXY(interface->sprites[BAG_SPRITE_ITEM_HIGHLIGHT], OPAL_ITEM_HIGHLIGHT_X, OPAL_ITEM_HIGHLIGHT_Y +" in SPR
assert 'Graphics_LoadTilemapToBgLayerFromOpenNARC(controller->bagGraphicsNARC, bag_ui_main_NSCR' in MAIN
assert 'Graphics_LoadTilemapToBgLayerFromOpenNARC(controller->bagGraphicsNARC, pokeball_borders_NSCR' in MAIN
for count in (1,4,7,8):
    assert f"sPocketButtonTouchRectangles_{count}Pocket" in MAIN if count==1 else f"sPocketButtonTouchRectangles_{count}Pockets" in MAIN
assert "sDialBtnTouchRect" in MAIN
assert 'for x,y in ((8,32),(16,80),(40,120),(80,144),' in ART
assert 'panel(p,112,6,139,150,4,1)' in ART
assert 'panel(p,4,147,247,35,4,1)' in ART
print("PASS: native Bag nine-row list, description, sprite and touch geometry unchanged")
print("PASS: V3 BG art decorates those existing screen positions")
