#!/usr/bin/env python3
"""Regression checks for B1 cinematic-only native move script additions."""
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[2]
for move, resource_id, emitter_id in (("shadow_ball", "0", "3"), ("thunderbolt", "0", "1"), ("ice_beam", "0", "0"), ("flamethrower", "0", "0"), ("energy_ball", "0", "2")):
    source = (ROOT / "res" / "moves" / move / "anim.s").read_text()
    assert source.count("B1:") == 1, f"{move}: B1 effect missing"
    assert len(re.findall(rf"CreateEmitter {resource_id}, {emitter_id}, EMITTER_CB_SET_POS_TO_DEFENDER", source)) >= 2
    assert source.count("LoadParticleResource 0,") == 1
    assert source.count("WaitForAllEmitters") == 1
    assert source.count("UnloadParticleSystem 0") == 1
    assert source.index("WaitForAllEmitters") < source.index("UnloadParticleSystem 0")
    assert source.rstrip().endswith("End")
    assert "Func_FadeBg FADE_BG_TYPE_BASE, 1," in source
    fades = re.findall(r"Func_FadeBg FADE_BG_TYPE_BASE, 1, (\d+), (\d+),", source)
    assert fades and fades[-1][1] == "0", f"{move}: scene fade must reset"

# Additional B1 pilots without global tint: verify effect sequencing and cleanup.
for move in ("sludge_bomb", "stone_edge"):
    source = (ROOT / "res" / "moves" / move / "anim.s").read_text()
    assert source.count("B1:") == 1, f"{move}: B1 impact layer missing"
    assert source.count("CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER") >= 2
    assert "WaitForAllEmitters" in source and "UnloadParticleSystem 0" in source
    assert source.index("WaitForAllEmitters") < source.index("UnloadParticleSystem 0")
    assert source.rstrip().endswith("End")

print("PASS: B1 seven cinematic pilots preserve native emitter and cleanup contracts")

# Dragon Pulse uses generic particles requiring their existing native extra parameters.
dragon = (ROOT / "res/moves/dragon_pulse/anim.s").read_text()
assert dragon.count("B1:") == 1
assert dragon.count("CreateEmitter 0, 3, EMITTER_CB_GENERIC") == 2
assert dragon.count("SetExtraParams 0, 2, 26, 20, 0, 0") == 2
assert dragon.index("WaitForAllEmitters") < dragon.index("UnloadParticleSystem 0")
assert dragon.count("LoadParticleResource 0, dragon_pulse_spa") == 1
