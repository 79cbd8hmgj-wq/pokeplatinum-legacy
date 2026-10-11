# Opal B2–B8 cinematic battle presentation (PR #110)

Visual-only. No move data, damage, accuracy, targeting, AI, RNG, status, weather rules, encounter tables or save/event flags are changed.
Everything is driven by the existing move/common animation scripts, which the engine only runs after it has decided the outcome.

## Evidence tiers (never conflate)

| Tier | Meaning | Status of this PR |
|---|---|---|
| designed | recipe / manifest only | done earlier (B1 handoff + `pokemon_opal_pr110_b2_b8_*` package) |
| source-installed | C, macros, graphics, scripts wired into the build | **done** (B2–B8) |
| source-validated | static / symbolic / property checks pass | **done** — see `.github/workflows/validate-opal-b2-b8.yml` |
| build-verified | both US revisions build | see `IMPLEMENTATION_REPORT.md` for the exact commands and results |
| runtime-accepted | owner confirms on emulator/hardware | **not done — owner action**, sheet: `EMULATOR_QA.md` |

## Layout

| Path | What |
|---|---|
| `src/battle_anim/opal_cinematic.c`, `include/battle_anim/opal_cinematic{,_math}.h` | `SPRITE_FUNC_OPAL_FX` (anchor / travel / burst / trail sprite) and `Func_OpalCamera` (backdrop parallax / punch) |
| `asm/macros/btlanim_opal.inc` | the cue vocabulary: `OpalChargeAura`, `OpalProjectile`, `OpalImpactBurst`, `OpalResidual`, `OpalCam*`, `OpalDimIn/Out`, `OpalLightPulse`, `OpalWeatherAccent*`, `OpalReact*` |
| `res/moves/*/anim.s`, `res/battle/scripts/common_anims/*.s` | the composites (see `move_template_map.json`) |
| `tools/visual_overhaul/opal_fx/` | donor sheet builder (Emerald PNG → DS cells), installer, recipes |
| `docs/visual_overhaul/opal_installed_fx/` | per-sheet provenance (donor path + sha256, conversion, palette, tiles) |
| `tools/visual_overhaul/opal_cue_trace.py` | symbolic cue-trace validator (every control-flow path) |
| `tools/visual_overhaul/validate_opal_assets.py`, `test_opal_cinematic_math.c` | asset gate and host math property test |
| `tools/visual_overhaul/build_opal_b2_b8_reports.py` | regenerates `source_map.json`, `donor_assets_used.json`, `move_template_map.json`, `fx_sheets_preview.png` (`--check` in CI) |
| `tools/visual_overhaul/opal_budget_report.py` | resource peaks + archive deltas → `BUDGET_TABLES.md` |

## Accessibility / safety switches (compile-time, `include/constants/battle/battle_anim.h`)

* `OPAL_LOW_FLASH 1` — every backdrop dim/pulse runs at half strength; nothing brighter than a pale tint.
* `OPAL_REDUCED_MOTION 1` — camera cues are compiled out; FX pop/shrink/drift are disabled.
* No cue alternates faster than once per 6 frames; the strongest light pulse is peak 4 of 16 (2 under low-flash) for ≈ 10 frames; the deepest dim is level 10 of 16 reached over ≥ 10 frames. None touches healthboxes or text.
* The in-game *Battle Scene: Off* option skips the animation (and every cue in it) because the engine never calls it.

## Validate locally

```sh
python3 tools/visual_overhaul/opal_cue_trace.py --baseline docs/visual_overhaul/opal_b2_b8/cue_trace_baseline.json
python3 tools/visual_overhaul/opal_cue_trace.py --define OPAL_LOW_FLASH=1 --define OPAL_REDUCED_MOTION=1
python3 tools/visual_overhaul/validate_opal_assets.py           # POKEEMERALD_ROOT=<pokeemerald checkout> enables the byte-identical rebuild
python3 tools/visual_overhaul/build_opal_b2_b8_reports.py --check
gcc -I include -o /tmp/t tools/visual_overhaul/test_opal_cinematic_math.c && /tmp/t
```
