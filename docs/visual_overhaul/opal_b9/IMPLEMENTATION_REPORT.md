# Opal B9 P0 — implementation report

Base: `main` @ `6b1ee43a` (merged PR #110). Branch `claude/pokemon-opal-b9-t63961`. Scope: P0 (19 early moves) only; P1/P2 deferred (see "Not implemented").

**Runtime status: nothing here has been run in an emulator or on hardware.** Every visual statement in `RECIPES.md` is a design claim until `EMULATOR_QA.md` has been executed.

## What changed

* 19 move scripts rewritten as Opal composites over their native emitters: `res/moves/{tackle,scratch,pound,quick_attack,bite,ember,water_gun,bubble,vine_whip,razor_leaf,thunder_shock,powder_snow,gust,peck,rock_throw,confusion,growl,leer,tail_whip}/anim.s`
* 7 new FX sheets (`res/graphics/battle/moves/opal_b9_{strike,ember,nature,wind,rock,bubble,sense}` + `opal_b9_wind_ice` palette), recipes in `tools/visual_overhaul/opal_fx/recipes/`, NARC order + meson lists updated by the B2 installer, provenance in `docs/visual_overhaul/opal_installed_fx/`
* `asm/macros/btlanim_opal.inc`: sequence constants only (no new cue macro, **no C / engine change**)
* Tooling: `opal_cue_trace.py` and `validate_opal_assets.py` accept B1 Ranger sheets driven through `OpalFx` (needed for Rock Throw); new `tools/visual_overhaul/opal_b9/{make_b9_recipes,build_candidate_matrix}.py`; CI workflow `validate-opal-b2-b8.yml` triggers on the new paths and runs the matrix check
* Evidence regenerated: `cue_trace_baseline.json` (29 PR #110 entries unchanged, +19), `source_map/donor_assets_used/move_template_map.json`
* No change to any `data.json`, battle script, effect script, learnset or table.

## Validation performed

Source commit for the results: the head of this branch's code commits (docs-only commits follow).

| Check | Command | Result |
|---|---|---|
| Sheet registration / budgets / deterministic rebuild from the Emerald tree | `python3 tools/visual_overhaul/validate_opal_assets.py` | PASS — 14 sheets (7 new, each rebuilt byte-identical), 67 script resource references |
| Cue trace, every control-flow path, 48 scripts | `python3 tools/visual_overhaul/opal_cue_trace.py --baseline docs/visual_overhaul/opal_b2_b8/cue_trace_baseline.json` | PASS, baseline identical |
| Cue trace, low-flash and low-flash + reduced-motion | `… --define OPAL_LOW_FLASH=1` / `… --define OPAL_LOW_FLASH=1 --define OPAL_REDUCED_MOTION=1` | PASS ×2 |
| Camera/FX math property test | `gcc -Wall -Wextra -Werror -I include -o /tmp/t tools/visual_overhaul/test_opal_cinematic_math.c && /tmp/t` | PASS (1,572,385 cases) |
| Evidence files current | `python3 tools/visual_overhaul/build_opal_b2_b8_reports.py --check` | PASS |
| Candidate matrix current | `python3 tools/visual_overhaul/opal_b9/build_candidate_matrix.py --check` | PASS |
| B1 / AV1 / G7 contracts | `validate_b1_cinematic_pilots.py`, `validate_b1_existing_battle_integration.py`, `validate_av1_battle_presentation.py`, `validate_b1_installed_donor_sprites.py` | PASS ×4 (Ember / ThunderShock / Powder Snow still satisfy the AV1 contract) |
| US Rev 1 build (clean) | `make configure ROM_REVISION=1 BUILD=/var/tmp/pp_rev1 && make rom ROM_REVISION=1 BUILD=/var/tmp/pp_rev1` | success, ROM sha256 `6dc4bcdf42b7eebf52650f6208741be18f1f6596e5fe33affa03a05b000cefbe` |
| US Rev 0 build | `make configure ROM_REVISION=0 BUILD=/var/tmp/pp_rev0 && make rom ROM_REVISION=0 BUILD=/var/tmp/pp_rev0` | success, ROM sha256 `3f072bceb189570365fc305a5bc1b75b1697306537a3df99470cb0690ecf19ae` |
| Low-flash + reduced-motion compile | same Rev 1 build with `OPAL_LOW_FLASH 1`, `OPAL_REDUCED_MOTION 1` (header reverted afterwards) | compiles and links |
| CI `build (US rev 0/1)` | GitHub Actions on the PR | see the PR checks |

Local toolchain note (environment only, nothing committed): the sandbox proxy blocks `wrapdb.mesonbuild.com`; the rapidjson/yyjson wrap patches were fetched from the identical
GitHub-release URLs into `subprojects/packagecache` (hash-verified against the `.wrap` files). Rev 1 was built twice from clean build directories and produced the identical ROM hash above. (An *incremental* rebuild after temporarily flipping `OPAL_LOW_FLASH` / `OPAL_REDUCED_MOTION` and reverting them produced a different hash — the incremental dependency tracking evidently does not fully re-process the cpp-included script headers — so always compare ROMs from clean build directories. The CI artifacts are authoritative.)

## Static resource bounds (upper bounds from symbolic execution — **not measurements**)

Policy caps enforced by the cue trace: ≤ 2 managers, ≤ 40 OAM entries, ≤ 400 OBJ char tiles per script. (`docs/visual_overhaul/opal_b2_b8/PERFORMANCE_AUDIT.md` explains why these are bounds.)

| Script | paths | frames (lower bound) | sprite managers | live Opal FX sprites | OAM entries (bound) | OBJ char tiles |
| tackle | 1 | 20 | 2 | 1 | 4 | 262 |
| scratch | 1 | 14 | 1 | 4 | 4 | 184 |
| pound | 1 | 10 | 2 | 2 | 5 | 368 |
| quick_attack | 1 | 27 | 2 | 4 | 16 | 262 |
| bite | 1 | 20 | 1 | 2 | 2 | 184 |
| ember | 1 | 49 | 2 | 3 | 3 | 292 |
| water_gun | 3 | 30 | 1 | 11 | 11 | 90 |
| bubble | 2 | 33 | 1 | 6 | 6 | 98 |
| vine_whip | 1 | 29 | 1 | 3 | 3 | 106 |
| razor_leaf | 1 | 108 | 1 | 6 | 6 | 106 |
| thunder_shock | 1 | 63 | 2 | 3 | 3 | 163 |
| powder_snow | 1 | 91 | 2 | 2 | 8 | 150 |
| gust | 1 | 44 | 2 | 4 | 12 | 184 |
| peck | 1 | 12 | 2 | 2 | 5 | 262 |
| rock_throw | 1 | 44 | 2 | 3 | 5 | 303 |
| confusion | 1 | 20 | 1 | 2 | 8 | 184 |
| growl | 1 | 24 | 2 | 8 | 14 | 312 |
| leer | 2 | 36 | 1 | 2 | 2 | 128 |
| tail_whip | 1 | 24 | 2 | 3 | 8 | 129 |

Highest pressure: Pound (368 OBJ tiles: STRIKE 184 + ring 184, cap 400), Growl (312), Rock Throw (303 incl. the 219-tile Ranger sheet). New sheets cost 56–184 tiles each, ≤ 15 colours, one OBJ palette slot per loaded manager.
ROM growth: the seven sheets are small 4bpp NCGR/NCER/NANR/NCLR members of the existing move-graphics NARCs; exact NARC sizes of the built ROM are in `opal_budget_report.py --build <dir>` output, no base-build delta was taken.

## Deviations from the supplied spec / handoff

1. **Not emulator-verified.** The spec's definition of done ("only mark moves tested after screenshots/video or emulator QA") is therefore *not* met; all moves are `source-passed` only. No emulator is available in this environment.
2. **Handoff text references `…manifest_v1.json` and "PR #110 head"**; I used the delivered `v2` manifest and merged `main`. The manifest's `source_animation: "locate_in_pr110_head"` was resolved against the current `res/moves/<move>/anim.s` files.
3. **Contest branches** of Water Gun, Bubble and Leer are left fully native (no Opal cue). The other 16 scripts have no contest branch, so their cues also run in contests — unverified (QA scenario B9-CONTEST).
4. **Not every move is a "full new animation".** Following "reuse existing infrastructure / preserve battle timing", every script keeps its native emitters and delays and layers move-specific sprite choreography on top. The candidate native particle art itself (SPL archives) is unchanged.
5. **Reaction change:** Tackle, Scratch, Pound, Bite, Vine Whip, Razor Leaf use `OpalReactLight` in place of the native bare shake (same frame and recoil, plus one white flash); **Peck gains** a light recoil it did not have. Quick Attack, Water Gun, Bubble, Gust, Rock Throw, Powder Snow, Thunder Shock, Ember keep their native shakes/flashes.
6. **Tail Whip** native 2-iteration `BeginLoop` is unrolled into two copies (same sounds/revolves) so the target pulse can attach to the second wag.
7. **Bite** now ends with `WaitForAllEmitters` + `UnloadParticleSystem 0` (engine `End` already did both) because the cue-trace invariant requires explicit particle unload.
8. **Scratch** adds 2 + 2 frames of `Delay` before its final `WaitForAllEmitters` (≤ +4 frames only if the native emitters are shorter than that).
9. **Razor Leaf** fan timing is aligned by arithmetic to the native impact frame (75) — the native leaf flight itself is inside an SPL emitter whose timeline I could not inspect; verify visually.
10. **Bite doubling risk:** the native `bite_spa` may already draw jaws; both are kept (QA row).
11. Spec items not applicable to P0 and therefore not built: weather accents (P0 manifest has none), persistent per-turn effects, new renderer primitives (the existing `SPRITE_FUNC_OPAL_FX` was sufficient; rotation is not supported by it, so mirrored art is baked into the sheets as flipped frames).
12. Camera cues are used only where B3 policy allows (Pound, Rock Throw: no native base-BG shake in those scripts).

## Not implemented / deferred

* **P1 (19 moves) and P2 (14 moves)** — deliberately not started (handoff: stop after P0 for review).
* HGSS, Ranger (beyond the B1 installs), PMD-Sky and Ruby/Sapphire art: not usable/available in this workspace at frame level (see `CANDIDATE_MATRIX.md` §1). FireRed's sprite set is byte-identical to Emerald's, so it adds nothing beyond the Emerald files.
* No frame-time / VBlank-DMA measurement, no hardware test, no screenshots (the sheet previews are static PNG renders only).
* Donor redistribution/licence terms were **not** verified: all pokeemerald/pokefirered/pokeranger2 art is third-party Nintendo/Game Freak material; provenance is by path + sha256 only.

## Risks to watch in QA

Bite jaw doubling · Razor Leaf arrival vs native leaves · cues in contests · two OBJ palette slots per script in busy doubles scenes · `OpalReactLight` flash on frequently repeated moves (consider dropping it for Tackle if it reads as too busy).
