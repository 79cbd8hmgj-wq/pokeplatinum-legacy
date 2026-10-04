# G7 — Final Closure Summary

**Question: what does the complete G7 visual overhaul now contain?**

Status: **CLOSED** with G7.7 (PR #60). Remaining items are owner runtime/visual sign-off only
(see `G7_7_FINAL_COHESION_REPORT.md` §8). Everything is palette/art/data driven; no engine, gameplay,
script, event, encounter, geometry, collision, camera or renderer change was made by G7.

| Phase | Contents | Authority |
|---|---|---|
| G7.1A | Battle command menu: modern button banks, label plates, monotonic ramps, empty-slot distinction | `generate_battle_command_ui.py` |
| G7.1B | Move selection: type-hued move palettes, PP/label contrast, selected vs unselected states | `generate_move_select_palettes.py`, `move_palettes.c` |
| G7.2A | Healthboxes (enemy / player singles / doubles): steel panel, white-on-fill ≥ 7:1, HP/status legibility | `generate_battle_ui.py` |
| G7.2B | 20 message frames with unified light/dark treatment | `generate_message_frames.py` |
| G7.3 | Encounter intensity hierarchy (normal < important < boss/legendary); risky runtime-sensitive additions deliberately deferred | `G7_3_ENCOUNTER_TIER_AUDIT.md` |
| G7.4 | Core menus: Party, Summary, Bag, Start, Shop — shape-cue focus states, firmer chrome, shared gold focus accent (Party/Bag/Shop) | `generate_*_ui.py` |
| G7.5 | Global windows: system/field window frames, scroll cursor and wait dial contrast across all 20 frames | `generate_ui_foundation.py` |
| G7.6 | Overworld atmosphere for seven families (Eterna, snow, Galactic, Coronet/Spear Pillar, Distortion, lakes/coast, caves/Turnback): palette-only texture grades, isolated lighting sets 015–019, fog tuning, G4 outdoors-lighting classification fix | `generate_g76_atmosphere.py` |
| G7.7 | Integration pass: lighting hierarchy fix (caves softened, Spear Pillar strengthened), core-menu validator EOL fix, ownership audit to map-header level, closure validator, CI wiring of all G7 validators | `validate_g77_final_cohesion.py`, `g7-visual-validation.yml` |

Standing guarantees (CI-enforced): graded textures are palette-only with unchanged names/dimensions/texels;
lighting keyframe structure unchanged; generators derive from pinned baselines and are idempotent;
ordinary retail lighting/texture sets untouched; visual intensity orders ordinary ≤ standard ≤ special;
every consumer of a graded resource is audited; no non-visual path changes.

Deferred by design (not defects): NSBMD-embedded prop textures, snow particle density, Verity/Valor/Sendoff
per-lake differentiation (shared area record), Iron Island/Snowpoint Temple/Lost Tower grading, recolouring the
Start/Summary retail focus accents (shared palette banks), battle-background resource retouching.
