#!/usr/bin/env python3
"""Heuristic, read-only move-animation script inventory for B2-B8.

Counts are NOT a control-flow proof: doubles, Contest and friendly-fire branches
may legitimately allocate and free resources in each alternative path.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re

OPS = ("LoadParticleResource", "UnloadParticleSystem", "WaitForAllEmitters",
       "InitSpriteManager", "FreeSpriteManager",
       "InitPokemonSpriteManager", "FreePokemonSpriteManager",
       "SwitchBg", "RestoreBg", "Func_FadeBg", "Func_FadeBattlerSprite",
       "Func_Shake", "Func_ShakeBg", "Func_ScrollCustomBg", "CreateEmitter",
       "CreateEmitterEx", "CreateEmitterForMove", "CreateEmitterForFriendlyFire",
       "JumpIfContest", "JumpIfFriendlyFire", "JumpIfBattlerSide",
       "PlaySoundEffectR", "PlaySoundEffectL", "PlayMovingSoundEffectAtkDef",
       "Call", "Return", "End", "Delay")

def inspect(script):
    counts = Counter()
    labels = []
    for raw in script.splitlines():
        line = raw.split("//", 1)[0].strip()
        if not line or line.startswith("#"):
            continue
        if line.endswith(":"):
            labels.append(line[:-1])
            continue
        match = re.match(r"([A-Za-z][\w]*)\b", line)
        if match:
            counts[match.group(1)] += 1
    flags = []
    for load, free, name in (
        ("LoadParticleResource", "UnloadParticleSystem", "particle_unload_review"),
        ("InitSpriteManager", "FreeSpriteManager", "sprite_manager_free_review"),
        ("InitPokemonSpriteManager", "FreePokemonSpriteManager", "pokemon_manager_free_review"),
        ("SwitchBg", "RestoreBg", "bg_restore_review")
    ):
        if counts[load] and not counts[free]:
            flags.append(name)
    if counts["JumpIfContest"] or counts["JumpIfFriendlyFire"]:
        flags.append("branch_specific_cleanup_review")
    if counts["InitSpriteManager"] or counts["InitPokemonSpriteManager"]:
        flags.append("OBJ_and_healthbox_ownership_review")
    if counts["Func_FadeBg"] or counts["SwitchBg"]:
        flags.append("palette_and_scene_reset_review")
    if counts["End"] > 1:
        flags.append("multiple_script_exits_review")
    return {"labels": labels, "op_counts": {op:counts[op] for op in OPS if counts[op]},
            "heuristic_review_flags": flags}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--only-mapped", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    manifest = json.loads((root / "docs/visual_overhaul/B2_B8_IMPLEMENTATION_MANIFEST.json").read_text())
    mapped = defaultdict(list)
    for group in manifest["cinematic_archetypes"]:
        for move in group["moves"]:
            mapped[move].append(group["id"])
    paths = sorted((root/"res/moves").glob("*/anim.s"))
    assert paths, "No move animation scripts found"
    missing = sorted(set(mapped) - {path.parent.name for path in paths})
    result=[]
    for path in paths:
        if args.only_mapped and path.parent.name not in mapped:
            continue
        item=inspect(path.read_text())
        item.update(move=path.parent.name, path=str(path.relative_to(root)),
                    cinematic_archetypes=mapped.get(path.parent.name, []))
        result.append(item)
    data={"kind":"heuristic_source_inventory_not_runtime_proof",
          "scanned":len(result),"mapped_moves":len(mapped),
          "missing_mapped_scripts":missing,"moves":result}
    output=json.dumps(data, indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(output)
    else:
        print(output,end="")
    if missing:
        raise SystemExit("Missing mapped scripts: "+", ".join(missing))

if __name__ == "__main__":
    main()
