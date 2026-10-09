# AV1 — Animated Battle Presentation Batch

Opportunity IDs: **V06** (battle particle composites), **V09** (UI animation); Ranger 2 `IO-FX-PRIM` / `IO-FX-SEQ`.
Baseline: `main` @ `7443b929`. No move balance, mechanics, or `data.json` changes. G5 impact-shake work is untouched.

## Method

Platinum particle archives (`.spa`) are opaque SPL binaries and there is no in-repo SPL authoring tool, so AV1 did **not**
redraw particle textures. Instead it applies the IO-FX-SEQ idea (launch → impact → secondary → dissipate) natively in
`anim.s`, compositing *existing Platinum emitters* from sibling moves as secondary layers on a second particle system.
Every emitter index used is one already used at the same anchor (defender/generic) by the donor move. Redrawing Ranger
primitives into `.spa` textures remains deferred (see blockers).

## Change ledger — battle effects

| Family | Move | Resource | Change | Platinum emitter source / Ranger inspiration |
|---|---|---|---|---|
| Fire | Ember | `res/moves/ember/anim.s` | warm scene tint, secondary ember burst (two staggered emitters), orange defender glow decaying, tint fades out | `fire_punch.spa` emitters 0, 2; IO-FX-SEQ burst/ember/dissipate phasing |
| Fire | Fire Spin | `res/moves/fire_spin/anim.s` | pulsing heat-glow scene tint during vortex, trailing embers, dissipating orange fade | `flame_wheel.spa` emitters 1, 2 |
| Electric | Thunder Shock | `res/moves/thunder_shock/anim.s` | three-step branching arcs after primary strike, yellow impact accents on defender | `thunderbolt.spa` emitters 0, 1, 3 |
| Electric | Spark | `res/moves/spark/anim.s` | post-lunge discharge arc at impact plus a pale-yellow flash pulse | `discharge.spa` emitter 1 |
| Energy | Psybeam | `res/moves/psybeam/anim.s` | beam released as three staggered, shrinking pulses; breathing purple scene glow that settles on exit | own emitter 0, re-spawned with decreasing speed params |
| Energy | Swift | `res/moves/swift/anim.s` | trailing second star wave, scatter burst + defender flash at impact | own emitters 1 and 0, re-spawned |

Preserved: particle resources of the original move, sound sequence, damage/accuracy/effect data, defender shake and
sprite-fade calls, scene tint restoration (all `Func_FadeBg` tints return to 0 before `End`).

## Change ledger — animated UI

Generator: `tools/visual_overhaul/generate_av1_battle_ui_anim.py` (idempotent, `--check` mode). Only NANR JSON changed;
cells, pixels, palettes untouched (G5 recolors are not touched).

| Resource | Change | Inspiration |
|---|---|---|
| `res/graphics/battle/interface/cursor_anim.json` | each corner bracket gets a 3-frame lock-on snap-in (5px→1px) that replays whenever the cursor is repositioned/re-selected, then an eased (7/4/7/4-frame) breathing loop via `loopStartFrame`; same ±2px maximum as retail so text stays unobstructed; 4 sequences / 4 cells unchanged | Ranger 2 styler cursor snap; HGSS command cursor |
| `res/graphics/battle/healthbox/arrows_wide_anim.json` | active-battler marker keeps the retail cell sweep, hold phase becomes a 4-step 2px bob (cell + translate results) | PMD Sky selection-marker bob |

HP bar, status indicators, input handling and text drawing are not touched (no C or cell/pixel changes).

## Validation

- `python3 tools/visual_overhaul/validate_av1_battle_presentation.py` — script/system balance, emitter indices against
  SPL headers, `data.json` untouched, NANR consistency, generator freshness.
- CI: Rev 0 / Rev 1 US builds (see PR). Runtime/visual QA is owner-only and **not performed here**.

## Deferred / blockers (scope not expanded)

- Redrawn Ranger 2 primitives inside `.spa` textures: needs an SPL texture/emitter editor (none in repo). Remains V06.
- Healthbox `arrows_thin` and `top_stock` party-ball animations were reviewed; their sheets are frame-per-cell with
  C-side sequence selection, so no safe gain without new art. Deferred to V09.
- Possible VRAM contention from two simultaneous particle systems is unverified until owner runtime QA (Tri Attack and
  Blast Burn already run two systems).
- Roadmap `OPAL_POST_S2_DONOR_ROADMAP.md` otherwise unchanged (V06/V09 statuses annotated only).
