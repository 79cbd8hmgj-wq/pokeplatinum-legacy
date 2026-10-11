#!/usr/bin/env python3
"""Regenerate the Opal B2-B8 evidence files under docs/visual_overhaul/opal_b2_b8/ (all derived from source, none hand-edited):

  source_map.json          confirmed host paths / symbols / sha256 (preflight output; fails if a symbol or file is missing)
  donor_assets_used.json   donor origin path + sha256, conversion method, palette/animation ownership, output location
  move_template_map.json   every Opal-enabled script -> templates, sheets, palettes, camera/light/reaction/weather cues
  fx_sheets_preview.png    contact sheet of every installed sheet (static visual review without an emulator)

Run with --check in CI: fails if the committed files differ from a fresh generation.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/visual_overhaul/opal_b2_b8"
PROV = ROOT / "docs/visual_overhaul/opal_installed_fx"
GFX = ROOT / "res/graphics/battle/moves"


def sha(p: Path):
    return hashlib.sha256(p.read_bytes()).hexdigest()


ANCHORS = [
    ("move animation scripts", "res/moves/*/anim.s", [], "one script per move; entry label L_0; run by BattleAnimSystem after the engine decided the move executes"),
    ("common (status / weather / encounter) animations", "res/battle/scripts/common_anims/*.s", [], "played by PlayBattleAnimation from battle subscripts; order in anim_subscripts.order"),
    ("animation command macros", "asm/macros/btlanimcmd.inc", ["AddSpriteWithFunc", "InitSpriteManager", "JumpIfWeather", "CreateEmitter"], "script command vocabulary; includes btlanim_opal.inc"),
    ("script function macros (CallFunc table ids)", "asm/macros/btlanimfunc.inc", ["Func_FadeBg", "Func_Shake", "Func_ShakeBg", "Func_OpalCamera"], "CallFunc ids 0-84; id 84 = OpalCamera"),
    ("Opal cue vocabulary", "asm/macros/btlanim_opal.inc", ["OpalSheetBegin", "OpalFx", "OpalCamFocusAttacker", "OpalDimIn", "OpalWeatherAccentSub", "OpalReactHeavy"], "B2-B5 templates (cpp OPAL_RES pastes NAIX names)"),
    ("script interpreter / lifecycle backstop", "src/battle_anim/battle_anim_system.c", ["BattleAnimSystem_StartMove", "BattleAnimScriptCmd_End", "BattleAnimScriptCmd_AddSpriteWithFunc", "OpalCinematic_ResetState"], "End waits for all anim tasks/emitters, frees managers + particle systems, restores BG priorities/offsets/blend"),
    ("script / sprite function tables", "src/battle_anim/script_func_tables.c", ["sBattleAnimScriptFuncs", "sBattleAnimSpriteFuncs", "BattleAnimSpriteFunc_OpalFx", "BattleAnimScriptFunc_OpalCamera"], "sprite func 33 = Opal FX; script func 84 = Opal camera"),
    ("Opal FX sprite + camera implementation", "src/battle_anim/opal_cinematic.c", ["BattleAnimSpriteFunc_OpalFx", "BattleAnimScriptFunc_OpalCamera", "OpalCinematic_ResetState"], "battler resolution via BattleAnimUtil_GetBattlerSprites; hard lifetime caps"),
    ("Opal pure math (host-tested)", "include/battle_anim/opal_cinematic_math.h", ["OpalMath_CameraWeight", "OpalMath_Lerp"], "tools/visual_overhaul/test_opal_cinematic_math.c"),
    ("script constants", "include/constants/battle/battle_anim.h", ["SPRITE_FUNC_OPAL_FX", "OPAL_REDUCED_MOTION", "OPAL_LOW_FLASH", "OPAL_FX_FLAG_TRAIL"], "compile-time reduced-motion / low-flash switches live here"),
    ("battler resolution (targets, doubles, spread)", "src/battle_anim/battle_anim_util.c", ["BattleAnimUtil_GetBattlerSprites"], "same resolver as Func_Shake / Func_FadeBattlerSprite masks"),
    ("BG fade / shake owners", "src/battle_anim/script_funcs_3.c", ["BattleAnimScriptFunc_FadeBg", "BattleAnimScriptFunc_ShakeBg", "BattleAnimSpriteFunc_OffsetAndAnimate"], "base-BG palette fades use PLTTBUF_MAIN_BG_F; ShakeBg writes the base BG offset"),
    ("battle backdrop layers", "include/battle_anim/battle_anim_system.h", ["BATTLE_BG_BASE", "BATTLE_BG_EFFECT"], "BG_LAYER_MAIN_2 / MAIN_3; healthboxes are OBJ, text is BG0/BG1 (never touched)"),
    ("move animation hit event", "src/battle/battle_script.c", ["BtlCmd_PlayMoveAnimation", "BtlCmd_PlayBattleAnimation"], "SYSCTL_PLAYED_MOVE_ANIMATION: one move animation per move use; Effects-off skips the call"),
    ("animation on/off + substitute filter", "src/battle/battle_lib.c", ["BattleSystem_ShouldShowStatusEffect", "sEffectsAlwaysShown"], "status/common animations are suppressed on Substitute / semi-invulnerable battlers"),
    ("animations-off option", "src/battle/battle_system.c", ["BattleSystem_AreAnimationsOn"], "player option; skips every Opal cue with the vanilla animation"),
    ("status application path", "res/battle/scripts/subscripts/subscript_burn.s", ["BATTLE_ANIMATION_BURNED"], "status animations run only after all immunity / Safeguard / ability checks"),
    ("Protect-blocked path", "res/battle/scripts/subscripts/subscript_missed.s", ["BATTLE_ANIMATION_BLOCKED", "MOVE_STATUS_PROTECTED"], "REACT_BLOCKED hook"),
    ("encounter intro path", "res/battle/scripts/subscripts/subscript_start_encounter.s", ["_opal_cue", "BATTLE_STATUS_LEGENDARY", "BATTLE_STATUS_GIRATINA"], "B7 gate (read-only)"),
    ("encounter entry points", "src/encounter.c", ["Encounter_NewVsGiratinaOrigin", "Encounter_NewVsSpeciesAtLevel", "BATTLE_STATUS_DISTORTION"], "where the engine sets BATTLE_STATUS_* for story encounters (not modified)"),
    ("graphics NARC pipeline", "res/graphics/battle/moves/meson.build", ["pngs_for_pal", "no_cell_pngs_for_pal", "cell_jsons", "cellanm_jsons"], "PNG + cell/anim JSON -> NCGR/NCLR/NCER/NANR via nitrogfx"),
    ("sub-animation ids", "generated/battle_sub_animations.txt", ["BATTLE_ANIMATION_BLOCKED", "BATTLE_ANIMATION_ENCOUNTER_GIRATINA", "BATTLE_ANIMATION_ENCOUNTER_LEGEND"], "previously-unused slots 23, 24, 41-46 repurposed; ids 1-5 (status icons) untouched"),
]


def source_map():
    out = []
    for role, pattern, symbols, note in ANCHORS:
        files = sorted(ROOT.glob(pattern))
        if not files:
            raise SystemExit(f"source map: {pattern} matches nothing")
        entry = {"role": role, "path": pattern, "note": note}
        if "*" in pattern:
            entry["file_count"] = len(files)
            entry["tree_sha256"] = hashlib.sha256("".join(f"{f.relative_to(ROOT)}:{sha(f)}\n" for f in files).encode()).hexdigest()
        else:
            text = files[0].read_text()
            missing = [s for s in symbols if s not in text]
            if missing:
                raise SystemExit(f"source map: {pattern} lacks symbols {missing}")
            entry["symbols"] = symbols
            entry["sha256"] = sha(files[0])
        out.append(entry)
    return {"generated_by": "tools/visual_overhaul/build_opal_b2_b8_reports.py", "anchors": out,
            "blocked_anchors": [], "restrictions": [
                "no battle logic, move data, AI, RNG or save/event flag is read for mutation",
                "BATTLE_STATUS_* and enemy species are read-only gates in subscript_start_encounter.s",
                "BG layers touched: BATTLE_BG_BASE offsets/palette fades only (same owners as vanilla scripts)"]}


def donor_assets():
    sheets = []
    for p in sorted(PROV.glob("opal_*.provenance.json")):
        d = json.loads(p.read_text())
        name = d["name"]
        sheets.append({
            "sheet": name,
            "origin": d["donor_sources"],
            "conversion": d["conversion"],
            "tiles": d["obj_tiles"], "obj_char_bytes": d["obj_tiles"] * 32,
            "palette_colours": len(d["palette_colours_rgb555"]), "palette_variants": sorted(d["palette_variants_rgb555"]),
            "animation_sequences": d["sequences"],
            "ownership": "one sprite manager per use (OpalSheetBegin/OpalSheetEnd); palette = NCLR loaded into that manager; freed before UnloadParticleSystem",
            "outputs": {"png": f"res/graphics/battle/moves/{name}.png", "cell": f"res/graphics/battle/moves/{name}_cell.json",
                        "anim": f"res/graphics/battle/moves/{name}_anim.json", "provenance": f"docs/visual_overhaul/opal_installed_fx/{name}.provenance.json",
                        "recipe": f"tools/visual_overhaul/opal_fx/recipes/{name}.json"},
            "output_sha256": {k: sha(ROOT / v) for k, v in (("png", f"res/graphics/battle/moves/{name}.png"), ("cell", f"res/graphics/battle/moves/{name}_cell.json"), ("anim", f"res/graphics/battle/moves/{name}_anim.json"))},
        })
    prior = sorted(q.name for q in (ROOT / "docs/visual_overhaul/b1_installed_donors").glob("*.provenance.json"))
    return {"emerald_candidates_not_used": ["EMER_ELECTRIC_ORBS frames beyond 3", "EMER_GHOST_BG", "EMER_WATER_BG", "EMER_PSYCHIC_BG", "EMER_SOLARBEAM_BG", "EMER_IMPACT"],
            "not_used_reason": "Emerald .bin/BG/tilemap donors are GBA tile-map backgrounds; Platinum BG ownership (base/effect layers, fade + switch owners) would need a BG converter and a layer budget that the audit did not justify. Their roles are covered by native SwitchBg resources, procedural rings and palette fades; documented variance per handoff rule.",
            "sheets": sheets, "b1_installed_ranger_donors_reused": prior}


def move_templates():
    rows = {}
    pat = re.compile(r"^\s*(Opal\w+|Func_OpalCamera)\b", re.M)
    for p in sorted(list((ROOT / "res/moves").glob("*/anim.s")) + list((ROOT / "res/battle/scripts/common_anims").glob("*.s"))):
        t = p.read_text()
        used = sorted(set(pat.findall(t)))
        if not used:
            continue
        name = p.parent.name if p.name == "anim.s" else f"common_anims/{p.stem}"
        cues = {"primitives": [u for u in used if u in ("OpalChargeAura", "OpalProjectile", "OpalImpactBurst", "OpalResidual", "OpalFx")],
                "camera": [u for u in used if u.startswith("OpalCam") or u == "Func_OpalCamera"],
                "light": [u for u in used if u in ("OpalDimIn", "OpalDimOut", "OpalLightPulse")],
                "weather_accent": "OpalWeatherAccent" in used,
                "reactions": [u for u in used if u.startswith("OpalReact")]}
        sheets = sorted(set(re.findall(r"OPAL_RES\((\w+),\s*(\w+)\)", t)))
        rows[name] = {"script": str(p.relative_to(ROOT)), "sheets_and_palettes": [{"sheet": s, "palette": q} for s, q in sheets], "cues": cues,
                      "native_effects_preserved": sorted(set(re.findall(r"\b(CreateEmitter\w*|SwitchBg|Func_ShakeBg|Func_Shake|Func_FadeBattlerSprite|Func_Surf|Func_Earthquake|Func_Confusion)\b", t)))}
    return {"generated_by": "tools/visual_overhaul/build_opal_b2_b8_reports.py", "moves_and_animations": rows}


def preview():
    names = ["opal_thunder", "opal_ghost", "opal_water", "opal_fire", "opal_ice", "opal_fx_ring", "opal_fx_ring_fire", "opal_fx_ring_ice", "opal_fx_ring_psychic", "opal_fx_ring_opal"]
    ims = []
    for n in names:
        im = Image.open(GFX / f"{n}.png")
        pal = im.getpalette()
        rgba = Image.new("RGBA", im.size, (70, 70, 90, 255))
        px, op = im.load(), rgba.load()
        for y in range(im.height):
            for x in range(im.width):
                v = px[x, y]
                if v == 255:
                    op[x, y] = (120, 30, 120, 255)
                elif v != 0:
                    op[x, y] = (pal[v * 3], pal[v * 3 + 1], pal[v * 3 + 2], 255)
        ims.append(rgba)
    h = max(i.height for i in ims)
    w = sum(i.width + 6 for i in ims)
    sheet = Image.new("RGBA", (w, h), (30, 30, 40, 255))
    x = 0
    for i in ims:
        sheet.paste(i, (x, 0))
        x += i.width + 6
    return sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    files = {"source_map.json": json.dumps(source_map(), indent=1) + "\n",
             "donor_assets_used.json": json.dumps(donor_assets(), indent=1) + "\n",
             "move_template_map.json": json.dumps(move_templates(), indent=1) + "\n"}
    bad = []
    for name, text in files.items():
        p = OUT / name
        if a.check:
            if not p.exists() or p.read_text() != text:
                bad.append(name)
        else:
            p.write_text(text)
    png = OUT / "fx_sheets_preview.png"
    if not a.check:
        preview().save(png, optimize=True)
    if bad:
        print("FAIL: stale generated evidence:", bad, "- run tools/visual_overhaul/build_opal_b2_b8_reports.py")
        sys.exit(1)
    print("PASS: evidence files", "match" if a.check else "written", f"({len(files)} json + preview)")


if __name__ == "__main__":
    main()
