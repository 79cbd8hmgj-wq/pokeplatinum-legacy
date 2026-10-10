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
assert "#define OPAL_DESCRIPTION_TEXT_Y        4" in WIN
assert "OPAL_DESCRIPTION_TEXT_X, OPAL_DESCRIPTION_TEXT_Y, TEXT_SPEED_NO_TRANSFER" in WIN
assert "[BAG_SPRITE_ITEM] = {" in SPR
assert ".x = 24,\n        .y = 168," in SPR
assert "#define OPAL_MOVE_STATS_RIGHT_COL_X    104" in WIN
assert "#define OPAL_MOVE_STATS_VALUE_OFFSET   64" in WIN
assert "#define OPAL_CLOSE_BAG_TEXT_X          4" in WIN
assert "controller->stringBuffer, OPAL_MOVE_STATS_RIGHT_COL_X + OPAL_MOVE_STATS_VALUE_OFFSET" in WIN
assert "Window_Add(controller->bgConfig, &controller->windows[BAG_UI_WINDOW_ITEM_LIST], BG_LAYER_MAIN_2, OPAL_ITEM_LIST_TILE_X, OPAL_ITEM_LIST_TILE_Y, ITEM_LIST_WINDOW_WIDTH, ITEM_LIST_WINDOW_HEIGHT" in WIN
assert "Window_Add(controller->bgConfig, &controller->windows[BAG_UI_WINDOW_ITEM_DESCRIPTION], BG_LAYER_MAIN_0, OPAL_DESCRIPTION_TILE_X, OPAL_DESCRIPTION_TILE_Y, ITEM_DESCRIPTION_WINDOW_WIDTH, ITEM_DESCRIPTION_WINDOW_HEIGHT" in WIN
assert 'ManagedSprite_SetPositionXY(interface->sprites[BAG_SPRITE_ITEM_HIGHLIGHT], 177, 24 +' in SPR
assert 'Graphics_LoadTilemapToBgLayerFromOpenNARC(controller->bagGraphicsNARC, bag_ui_main_NSCR' in MAIN
assert 'Graphics_LoadTilemapToBgLayerFromOpenNARC(controller->bagGraphicsNARC, pokeball_borders_NSCR' in MAIN
for count in (1,4,7,8):
    assert f"sPocketButtonTouchRectangles_{count}Pocket" in MAIN if count==1 else f"sPocketButtonTouchRectangles_{count}Pockets" in MAIN
assert "sDialBtnTouchRect" in MAIN
assert 'panel(p,8,30,240,144,7,3)' in ART
assert '# painting eight permanent buttons here creates false controls.' in ART
assert 'panel(p,112,6,139,150,4,1)' in ART
assert 'panel(p,4,147,247,35,4,1)' in ART
print("PASS: native Bag nine-row list, description, sprite and touch geometry unchanged")
print("PASS: V3 BG art decorates those existing screen positions")
