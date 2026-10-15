#!/usr/bin/env python3
"""Guard real scroll graphics loading; map tile provenance requires separate audit."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
src = (ROOT / "src/applications/pokedex/ov21_021D5AEC.c").read_text()
graphics = (ROOT / "src/applications/pokedex/pokedex_graphics.c").read_text()

def require(pattern: str, where: str):
    assert re.search(pattern, src, re.S), f"Missing scroll runtime contract: {where}"

require(r"PokedexGraphics_LoadGraphicNarcCharacterData\s*\(\s*param0\s*,\s*scroll_main_background_NCGR_lz\s*,\s*param0->bgConfig\s*,\s*3\s*,\s*0\s*,", "main BG3 character load at tileStart 0")
require(r"PokedexGraphics_LoadGraphicNarcCharacterData\s*\(\s*param1\s*,\s*scroll_main_background_NCGR_lz\s*,\s*param1->bgConfig\s*,\s*2\s*,\s*0\s*,", "main BG2 character load at tileStart 0")
require(r"PokedexGraphics_GetGraphicNarcTilemapData\s*\(\s*param0\s*,\s*scroll_main_background_NSCR_lz\s*,", "scroll BG3 map archive fetch")
require(r"Bg_LoadToTilemapRect\s*\(\s*param0->bgConfig\s*,\s*3\s*,\s*v1->rawData\s*,\s*0\s*,\s*0\s*,", "scroll BG3 tilemap load")
require(r"Bg_LoadToTilemapRect\s*\(\s*param0->bgConfig\s*,\s*3\s*,\s*v1->rawData\s*,\s*1\s*,\s*4\s*,", "registered species overlay map")
require(r"search_national_NSCR_lz\s*;", "National mode map")
require(r"search_sinnoh_NSCR_lz\s*;", "Sinnoh mode map")
assert "Bg_LoadTiles(bgConfig, bgLayer, charData->pRawData, size, tileStart);" in graphics
print("PASS: Pokédex scroll runtime loader remains unchanged (BG2/BG3, char tileStart=0)")
