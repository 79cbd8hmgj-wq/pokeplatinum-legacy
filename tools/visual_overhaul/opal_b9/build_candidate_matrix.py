#!/usr/bin/env python3
"""Opal B9 cross-pool asset candidate matrix (spec: "Binding asset policy - all pools, every move").

Walks every donor/native pool that is actually present in this workspace, records what was searched, hashes every candidate that was
selected or seriously evaluated, and writes
    docs/visual_overhaul/opal_b9/candidate_matrix.json   (machine readable, committed)
    docs/visual_overhaul/opal_b9/CANDIDATE_MATRIX.md      (human readable, committed)

Rules: no path is written unless the file exists when the tool runs; a pool that is not in the workspace is recorded as
"unavailable". Selected donor files are derived from the installed recipes (tools/visual_overhaul/opal_fx/recipes/opal_b9_*.json).
`--check` (CI) re-derives the document and only requires that donor hashes still match when the donor tree is present.

  python3 tools/visual_overhaul/opal_b9/build_candidate_matrix.py [--check]
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WS = ROOT.parent  # workspace holding the donor checkouts
OUT = ROOT / "docs/visual_overhaul/opal_b9"
RECIPES = ROOT / "tools/visual_overhaul/opal_fx/recipes"


def sha(p: Path):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def count(root: Path, pattern: str):
    return sum(1 for _ in root.glob(pattern)) if root.is_dir() else None


def pools():
    P = []

    def pool(pid, label, root, scope, glob, status, note):
        r = WS / root if root else ROOT
        present = r.is_dir()
        P.append({"id": pid, "pool": label, "root": root or ".", "present": present,
                  "searched": scope if present else None, "files_in_scope": count(r, glob) if present else None,
                  "status": status if present else "unavailable in this workspace", "note": note})

    pool("native", "Platinum native (this repo)", None, "res/graphics/battle/moves/*.png", "res/graphics/battle/moves/*.png",
         "searched", "61 move sheets (+ native SPL particle archives, reused unchanged by every script). Evaluated: glare, scary_face, claw, vines, angry (see candidates).")
    pool("opal_b2b8", "Opal B2-B8 sheets (this repo)", None, "res/graphics/battle/moves/opal_*.png", "res/graphics/battle/moves/opal_*.png",
         "searched + reused", "water, ice, thunder, fire, ghost, ring (10 palettes), wx (4 palettes): reused by Water Gun, Powder Snow, Thunder Shock, Pound, Growl, Confusion, Tail Whip.")
    pool("ranger_b1", "Pokemon Ranger 2 via B1 installs (this repo)", None, "res/graphics/battle/moves/ranger_*.png", "res/graphics/battle/moves/ranger_*.png",
         "searched + reused", "ranger_rock_burst (Rock Throw impact); fire_bloom already owned by Ember; ice_bloom evaluated.")
    pool("emerald", "pokeemerald", "pokeemerald", "graphics/battle_anims/sprites/*.png", "graphics/battle_anims/sprites/*.png",
         "searched + primary donor", "indexed GBA frame strips, directly convertible with the B2 sheet builder.")
    pool("firered", "pokefirered", "pokefirered", "graphics/battle_anims/sprites/*.png", "graphics/battle_anims/sprites/*.png",
         "searched; byte-identical to pokeemerald for every shared file", "cmp over every shared PNG found no difference (only safari_bait.png is FR-only, irrelevant). Used as a deduplicated alias of the Emerald copies.")
    pool("crystal", "pokecrystal", "pokecrystal", "gfx/battle_anims/*.png", "gfx/battle_anims/*.png",
         "searched; evaluated, none selected", "2bpp 4-grey tile strips; frame layout lives in anim_obj asm, not in the PNG.")
    pool("yellow", "pokeyellow", "pokeyellow", "gfx/battle/move_anim_*.png", "gfx/battle/move_anim_*.png",
         "searched; evaluated, none selected", "128x40, 4 grey levels (L mode) tile sheets, same limits as Crystal.")
    pool("hgss", "pokeheartgold", "pokeheartgold", "files/**/*.png + *.narc", "files/**/*.narc",
         "searched; no decodable move-effect art in tree", "Battle particle archives are not part of the checkout (only the SPL header library). files/pbr/*.narc are opaque NARCs whose frames were not decoded - not inspected, not used.")
    pool("ranger2", "pokeranger2", "pokeranger2", "res/prebuilt/data/field/effect/*", "res/prebuilt/data/field/effect/*",
         "searched at package level only", "ef*/ew* LZ packages exist but only e002/e009/e010 were decoded in B1 (via tools/visual_overhaul/export_b1_ranger_effect_cells.py). No further packages were decoded for B9.")
    pool("pmd_sky", "pmd-sky", "pmd-sky", "files/EFFECT/effect.bin", "files/EFFECT/*",
         "searched at container level only", "effect.bin is a packed container with no extracted frames in the tree; frame-level inspection was not performed.")
    P.append({"id": "ruby_sapphire", "pool": "pokeruby / Ruby-Sapphire", "root": "pokeruby", "present": (WS / "pokeruby").is_dir(),
              "searched": None, "files_in_scope": None, "status": "unavailable in this workspace",
              "note": "no checkout present; Emerald (same engine lineage, same sprite set) was used instead."})
    P.append({"id": "procedural", "pool": "Opal procedural generators", "root": "tools/visual_overhaul/opal_fx/build_opal_fx_sheet.py", "present": True,
              "searched": "ring / star / dot generators", "files_in_scope": 3, "status": "reused (opal_fx_ring, opal_fx_wx)",
              "note": "no new procedural art was needed for B9 P0."})
    return P


def selected():
    rows = []
    for rp in sorted(RECIPES.glob("opal_b9_*.json")):
        r = json.loads(rp.read_text())
        frames_by_src = {}
        for f in r["frames"]:
            frames_by_src.setdefault(f["src"], []).append(f["id"])
        for sid, s in r["sources"].items():
            p = WS / "pokeemerald" / s["path"]
            rows.append({"decision": "selected", "sheet": r["name"], "pool": "emerald (== firered)", "path": f"pokeemerald/{s['path']}",
                         "exists": p.exists(), "sha256": sha(p) if p.exists() else None, "frames_used": frames_by_src.get(sid, []),
                         "variant": s.get("ramp") and "luminance-ramp recolour" or "as-is"})
    return rows


EVALUATED = [
    # (pool, path relative to workspace root, decision, reason)
    ("native", None, "res/graphics/battle/moves/glare.png", "rejected for Leer", "Glare's own sprite function and red slit eyes would make Leer read as Glare (spec: Leer must stay distinct and light); the 128px sheet would also cost 2x the OAM of the chosen 32px glint."),
    ("native", None, "res/graphics/battle/moves/claw.png", "rejected for Scratch", "Native metal-claw sprite drives Dragon Claw / Crush Claw through SPRITE_FUNC_METAL_CLAW; reusing it would make Scratch look like those moves."),
    ("native", None, "res/graphics/battle/moves/vines.png", "rejected for Vine Whip", "brown root sprite from the Grass Knot / Constrict family; Emerald vine_2 gives a green curl that animates as a lash."),
    ("ranger_b1", None, "res/graphics/battle/moves/ranger_ice_bloom.png", "rejected for Powder Snow", "a bright energy ball (Ice Beam family); Powder Snow needs scattered flecks and a sweeping swirl."),
    ("ranger_b1", None, "res/graphics/battle/moves/ranger_rock_burst.png", "selected for Rock Throw impact", "9-frame grit puff, already installed and budgeted by B1 (219 tiles); driven through OpalFx at 80% scale, translucent."),
    ("emerald", "pokeemerald", "graphics/battle_anims/sprites/scratch.png", "rejected for Scratch", "yellow crescent smear: reads as Slash/Cut. fury_swipes gives three distinct claw lines."),
    ("emerald", "pokeemerald", "graphics/battle_anims/sprites/claw_slash_2.png", "rejected for Scratch", "red droplet projectile frames, no arc."),
    ("emerald", "pokeemerald", "graphics/battle_anims/sprites/sharp_teeth.png", "rejected for Bite", "64x64 single frame (32 tiles) mostly empty; fangs.png gives two jaws for the same tile cost."),
    ("emerald", "pokeemerald", "graphics/battle_anims/sprites/eye.png", "rejected for Leer", "64x64 magenta eyeball (64 tiles) - too large and wrong colour for a quick repeated move."),
    ("emerald", "pokeemerald", "graphics/battle_anims/sprites/metal_sound_waves.png", "rejected for Growl", "spiky gold ring - reads as a Metal Sound / Screech effect."),
    ("emerald", "pokeemerald", "graphics/battle_anims/sprites/whirlwind_2.png", "rejected for Gust", "grey tornado column (Twister/Whirlwind); whirlwind.png sweep lines read as a gust."),
    ("emerald", "pokeemerald", "graphics/battle_anims/sprites/hail.png", "rejected for Powder Snow", "hail stone (Hail weather); snowball.png flecks are softer."),
    ("crystal", "pokecrystal", "gfx/battle_anims/whip.png", "rejected", "16x40, 4 grey levels (pokecrystal gfx/battle_anims/whip.png); Emerald vine_2 is the full-colour equivalent and needs no re-authoring of OAM layouts."),
    ("crystal", "pokecrystal", "gfx/battle_anims/speed.png", "rejected", "24x24, 3 levels, layout only in anim_obj asm; Emerald speed_dust / air_wave cover the role in colour."),
    ("crystal", "pokecrystal", "gfx/battle_anims/noise.png", "rejected", "24x80, 3 levels; Emerald noise_line / movement_waves cover the role in colour."),
    ("yellow", "pokeyellow", "gfx/battle/move_anim_0.png", "rejected", "128x40, 4 grey levels; Gen-1 tile sheet with no frame metadata in the PNG."),
]


def evaluated_rows():
    out = []
    for pool, root, rel, decision, reason in EVALUATED:
        p = (WS / root / rel) if root else (ROOT / rel)
        out.append({"decision": decision, "pool": pool, "path": (f"{root}/{rel}" if root else rel), "exists": p.exists(),
                    "sha256": sha(p) if p.exists() else None, "reason": reason})
    return out


MOVE_MATRIX = [
    # move, native kept, ingredients (pool: asset -> role)
    ("Tackle", "tackle_spa emitters, lunge", "emerald speed_dust -> dig-in dust; emerald hit -> impact flash"),
    ("Scratch", "scratch_spa emitters", "emerald fury_swipes (+hflip) -> three staggered claw arcs; emerald hit -> contact"),
    ("Pound", "pound_spa emitters", "emerald hit (large) -> contact; procedural ring (gold) -> pressure ring; B3 camera punch"),
    ("Quick Attack", "dash task, afterimages", "emerald air_wave -> trailing streak (3-copy trail); speed_dust -> launch dust; slash -> streak star impact"),
    ("Bite", "bite_spa emitters", "emerald fangs -> closing upper/lower jaw; hit -> snap flash"),
    ("Ember", "ember_spa, fire_punch_spa, Ranger fire bloom, base-BG tint", "emerald small_ember -> three-ember volley + cinders (Ranger bloom stays the impact)"),
    ("Water Gun", "water_gun_spa stream", "B2 opal_water (emerald water_droplet / water_impact) -> three droplet pulses + foam splash"),
    ("Bubble", "bubble_spa", "emerald bubble / small_bubbles / bubble_burst / bubble_burst_2 -> rising bubbles and pops"),
    ("Vine Whip", "vine_whip_spa, lunge", "emerald vine_2 -> thrown lash + second flick; leaf -> debris"),
    ("Razor Leaf", "razor_leaf_spa", "emerald leaf -> three-lane leaf fan; razor_leaf -> blade crescents; leaf -> flutter"),
    ("ThunderShock", "thunder_shock_spa + thunderbolt_spa, base-BG dim", "B2 opal_thunder (emerald electricity / electric_orbs) -> charge + burst; emerald spark_h -> jumping arcs"),
    ("Powder Snow", "powder_snow_spa, fades", "emerald whirlwind (ice recolour) -> swirl; emerald snowball -> flecks; B2 opal_ice -> frost glints"),
    ("Gust", "gust_spa, camera projection reset", "emerald air_wave / air_wave_2 -> streaks; whirlwind -> landing swirl; leaf -> debris"),
    ("Peck", "peck_spa, head tilt", "emerald air_wave -> thrust streak; emerald impact -> pierce star"),
    ("Rock Throw", "rock_throw_spa", "emerald rocks / flat_rock / flying_dirt -> boulder, shards, dirt; Ranger 2 e002 (B1) -> grit puff; B3 camera punch"),
    ("Confusion", "SwitchBg 20, mon-sprite warp", "procedural ring (psychic palette) -> concentric ripples; B5 magic pulse"),
    ("Growl", "growl_spa, cries", "procedural ring (gold) -> sound pulses; emerald movement_waves / noise_line -> sound arcs + roar jag"),
    ("Leer", "leer_spa, base-BG dim", "emerald leer -> eye glint on user and target"),
    ("Tail Whip", "revolve task, sounds", "emerald air_wave_2 -> wag crescents; procedural star (wx gold) -> feedback pulse"),
]


def build():
    return {"generated_by": "tools/visual_overhaul/opal_b9/build_candidate_matrix.py", "pools": pools(), "selected": selected(),
            "evaluated": evaluated_rows(), "per_move": [{"move": m, "native_kept": n, "ingredients": i} for m, n, i in MOVE_MATRIX]}


def markdown(d):
    L = ["# Opal B9 P0 - cross-pool candidate matrix", "",
         "Generated by `tools/visual_overhaul/opal_b9/build_candidate_matrix.py` from the workspace as it was when the tool ran. Paths and hashes below were read",
         "from real files; pools that were not present are marked unavailable. Nothing here is a runtime or visual verification.", "",
         "## 1. Pools searched", "", "| Pool | Present | Scope searched | Files in scope | Outcome | Note |", "|---|---|---|---:|---|---|"]
    for p in d["pools"]:
        L.append(f"| {p['pool']} | {'yes' if p['present'] else 'no'} | {p['searched'] or '-'} | {p['files_in_scope'] if p['files_in_scope'] is not None else '-'} | {p['status']} | {p['note']} |")
    L += ["", "## 2. Selected donor files (derived from the installed recipes)", "", "| Sheet | Donor file (pokeemerald; FireRed copy byte-identical) | sha256 | Frames used |", "|---|---|---|---|"]
    for r in d["selected"]:
        L.append(f"| {r['sheet']} | `{r['path']}` | `{(r['sha256'] or 'MISSING')[:16]}...` | {', '.join(r['frames_used'])} |")
    L += ["", "Full hashes: `candidate_matrix.json`; per-sheet conversion data: `docs/visual_overhaul/opal_installed_fx/opal_b9_*.provenance.json`.", "",
          "## 3. Evaluated candidates and decisions", "", "| Pool | Path | Decision | Reason |", "|---|---|---|---|"]
    for r in d["evaluated"]:
        L.append(f"| {r['pool']} | `{r['path']}`{'' if r['exists'] else ' (not present)'} | {r['decision']} | {r['reason']} |")
    L += ["", "## 4. Per-move recipe ingredients", "", "| Move | Native parts kept | Ingredients (pool asset -> role) |", "|---|---|---|"]
    for r in d["per_move"]:
        L.append(f"| {r['move']} | {r['native_kept']} | {r['ingredients']} |")
    L += ["", "Licence: all donor art is third-party (Nintendo / Game Freak decompilation outputs). Redistribution terms were not verified; see `IMPLEMENTATION_REPORT.md`.", ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    d = build()
    donors_here = (WS / "pokeemerald/graphics/battle_anims/sprites").is_dir()
    files = {"candidate_matrix.json": json.dumps(d, indent=1) + "\n", "CANDIDATE_MATRIX.md": markdown(d)}
    if a.check:
        if not donors_here:
            # CI has no donor tree: only verify the committed document is internally consistent with the installed recipes
            old = json.loads((OUT / "candidate_matrix.json").read_text())
            want = {(r["sheet"], r["path"]) for r in old["selected"]}
            have = {(rp.stem, f"pokeemerald/{s['path']}") for rp in RECIPES.glob("opal_b9_*.json") for s in json.loads(rp.read_text())["sources"].values()}
            if want != have:
                print("FAIL: candidate matrix does not list the donor files of the installed B9 recipes")
                sys.exit(1)
            print("PASS: candidate matrix consistent with recipes (donor tree not available; hashes not re-read)")
            return
        for n, t in files.items():
            if not (OUT / n).exists() or (OUT / n).read_text() != t:
                print(f"FAIL: {n} is stale - run tools/visual_overhaul/opal_b9/build_candidate_matrix.py")
                sys.exit(1)
        missing = [r["path"] for r in d["selected"] if not r["exists"]]
        if missing:
            print("FAIL: selected donor files missing:", missing)
            sys.exit(1)
        print("PASS: candidate matrix current; every selected donor file exists and is hashed")
        return
    for n, t in files.items():
        (OUT / n).write_text(t)
    print("wrote", ", ".join(files))


if __name__ == "__main__":
    main()
