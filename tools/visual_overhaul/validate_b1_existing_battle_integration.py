#!/usr/bin/env python3
"""Source-level safety checks for Opal's previously merged battle visuals.

This deliberately checks coexistence contracts without asserting emulator proof.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
def source(path):
    return (ROOT / path).read_text()

terrain = source("src/battle/terrain.c")
sub = source("src/battle/battle_subscreen.c")
anim = source("src/battle_anim/battle_anim_system.c")
particles = source("src/battle_anim/battle_particle_util.c")
previous = source("tools/visual_overhaul/validate_av1_battle_presentation.py")
assert "BattleSystem_GetRenderMode(battleSys) != 0" in terrain, "Terrain cycle must pause in menus"
assert "PaletteData_GetSelectedBuffersMask(paletteData)" in terrain, "Fade ownership guard missing"
assert "Terrain_RangeEquals(faded, unfaded, count)" in terrain, "Terrain palette tint ownership missing"
assert "Terrain_StopPaletteCycle" in terrain and "SysTask_Done(terrain->paletteTask)" in terrain, "Terrain cycle cleanup missing"
assert "PLTTBUF_MAIN_OBJ" in terrain and "PLTTBUF_MAIN_BG" in terrain, "Terrain main OBJ/BG mirror missing"
assert "PLTTBUF_SUB_BG" in sub and "subscreenPaletteBuf" in sub, "Subscreen palette ownership missing"
assert "BattleAnimScriptCmd_UnloadParticleSystem" in anim, "Particle unload handler missing"
assert "BattleAnimScriptCmd_SetDefaultAlphaBlending" in anim, "Default blending reset missing"
assert "VRAM_AUTO_RELEASE_TEXTURE_LNK" in particles and "VRAM_AUTO_RELEASE_PALETTE_LNK" in particles, "Particle auto-release flags missing"
for move in ("ember","fire_spin","thunder_shock","spark","psybeam","swift"):
    script = source(f"res/moves/{move}/anim.s")
    loads = re.findall(r"LoadParticleResource\s+(\d+),", script)
    unloads = re.findall(r"UnloadParticleSystem\s+(\d+)", script)
    assert loads, f"{move}: expected existing particle resource"
    assert sorted(set(loads)) == sorted(set(unloads)), f"{move}: unbalanced particle systems"
assert "UnloadParticleSystem" in previous, "Keep independent AV1 validation"
print("PASS: existing G7/AV1/S2-D presentation ownership and cleanup contracts")
