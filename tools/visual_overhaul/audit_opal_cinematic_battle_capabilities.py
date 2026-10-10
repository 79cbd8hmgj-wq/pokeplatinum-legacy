#!/usr/bin/env python3
"""Inventory native battle animation commands and current move-script usage.

Read-only, reproducible JSON suitable for comparing future cinematic batches.
"""
from collections import Counter
from pathlib import Path
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[2]
MACROS = ROOT / "asm/macros/btlanimcmd.inc"
if not MACROS.exists():
    MACROS = ROOT / "include/macros/btlanimcmd.inc"
if not MACROS.exists():
    MACROS = ROOT / "macros/btlanimcmd.inc"
assert MACROS.exists(), "Locate btlanimcmd.inc before auditing"
MOVE_DIR = ROOT / "res/moves"
assert MOVE_DIR.is_dir()
files = sorted(MOVE_DIR.glob("*/anim.s"))
assert files, "No move animation scripts found"
command_counter = Counter()
particle_scripts = []
special_effects = {}
for file in files:
    commands = []
    for line in file.read_text().splitlines():
        line = line.split("//", 1)[0].strip()
        if not line or line.startswith(("#", ".", "@")) or line.endswith(":"):
            continue
        word = re.match(r"([A-Za-z_][A-Za-z0-9_]*)", line)
        if not word:
            continue
        commands.append(word.group(1))
    command_counter.update(commands)
    if "LoadParticleResource" in commands:
        particle_scripts.append(str(file.relative_to(ROOT)))
    for name in ("Func_Shake", "Func_FadeBg", "CreateEmitter", "Func_MoveBattlerX2", "PlaySoundEffectL", "PlaySoundEffectR"):
        if name in commands:
            special_effects[name] = special_effects.get(name, 0) + 1
report = {
    "source": str(MACROS.relative_to(ROOT)),
    "script_count": len(files),
    "scripts_with_particle_resources": len(particle_scripts),
    "top_commands": command_counter.most_common(35),
    "effect_usage_script_count": special_effects,
    "av1_pilots": {
        name: str((MOVE_DIR / name / "anim.s").relative_to(ROOT))
        for name in ("ember", "fire_spin", "thunder_shock", "spark", "psybeam", "swift")
        if (MOVE_DIR / name / "anim.s").exists()
    },
}
assert report["script_count"] >= 100
assert len(report["av1_pilots"]) == 6
print(json.dumps(report, indent=2))
if __name__ == "__main__":
    pass
