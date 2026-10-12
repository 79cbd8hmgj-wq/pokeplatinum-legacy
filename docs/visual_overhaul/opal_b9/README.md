# Opal B9 — everyday-move cinematic expansion, slice P0 (19 early moves)

Presentation only. No move data, damage, accuracy, targeting, priority, AI, RNG, status, PP, learnset, or balance value is touched
(`git diff --stat -- res/moves/*/data.json` is empty). Everything runs inside the existing move animation scripts, which the engine only plays
**after** it has decided the move executes (and, for stat-drop moves, after the stat change succeeded — see "Outcome gating").

Inputs: `pokemon_opal_everyday_moves_b9_{spec,manifest,claude_handoff}_v2` (supplied package). Baseline: `main` @ `6b1ee43a` (merged PR #110).
Scope delivered: **P0_early_frequent, 19 moves.** P1 (19) and P2 (14) are intentionally **not** started — the handoff says to stop after P0 for review.

## Evidence tiers (never conflate)

| Tier | Meaning | Status |
|---|---|---|
| designed | spec / manifest | supplied package |
| source-installed | scripts, sheets, macros wired into the build | **done** (19 scripts, 7 sheets) |
| source-validated | static / symbolic / property checks | **done** (see `IMPLEMENTATION_REPORT.md`) |
| build-verified | both US revisions build | **done** (see `IMPLEMENTATION_REPORT.md` for exact commands and results) |
| emulator-tested | somebody ran it | **not done — owner action**, sheet: `EMULATOR_QA.md` |
| visual-approved | owner accepted the look | **not done — owner action** |

## Files

| Path | What |
|---|---|
| `CANDIDATE_MATRIX.md`, `candidate_matrix.json` | cross-pool asset inventory: pools searched / unavailable, every selected donor file with sha256, every evaluated-and-rejected candidate with a reason, per-move ingredients (generated: `tools/visual_overhaul/opal_b9/build_candidate_matrix.py [--check]`) |
| `FOLLOW_UP_ASSET_DECODING.md` | **open follow-up work** (HGSS / PMD / Ranger / Ruby-Sapphire decoding limits) that must be scheduled before the next animation batch |
| `RECIPES.md` | per move: host script, template, native parts kept, cue lifecycle, assets, timing, state gating, fallbacks |
| `EMULATOR_QA.md` | the emulator checklist you need to run (nothing here was run by the author) |
| `IMPLEMENTATION_REPORT.md` | validation commands + results, deviations, unimplemented items, risks |
| `../../../res/moves/<move>/anim.s` | the 19 rewritten scripts |
| `../../../res/graphics/battle/moves/opal_b9_*` | 7 new FX sheets (+ `opal_b9_wind_ice` palette variant); provenance in `../opal_installed_fx/opal_b9_*.provenance.json` |
| `../../../tools/visual_overhaul/opal_b9/make_b9_recipes.py` | writes the sheet recipes in `tools/visual_overhaul/opal_fx/recipes/opal_b9_*.json` (same builder/installer as B2) |
| `../../../asm/macros/btlanim_opal.inc` | adds the `OPAL_B9_*_SEQ_*` sequence constants; **no new cue macro and no engine/C change was needed** |

Cue-trace baseline (`../opal_b2_b8/cue_trace_baseline.json`) now covers 48 scripts: the 29 from PR #110 are byte-identical to before, 19 are new.
