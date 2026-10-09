# Visual Implementation and QA Ledger — 2026-10-09

Baseline: main dcbffe80839971f6233ef2553cc943c5a0dabebc. Source and merged-PR-history audit, NOT emulator or hardware validation.

Statuses: Source implemented = code/assets merged; not equivalent to runtime accepted. Catalog/research = candidate evidence, not gameplay implementation. No verified implementation means this audit found no feature-specific merged implementation; generic related work may exist.

| Feature | Wave | Current evidence | Next action |
|---|---:|---|---|
| IO-PREVIEW | 3 | No verified source implementation | Single-location pilot |
| IO-FOL-SHEETS | 3 | Catalog/research | Select subset |
| IO-PAL-CYCLE | 1 | Source implemented PR #79; runtime untested | Water/doubles/fades/time-of-day QA |
| IO-FOL-MECH | 5 | Roadmap only | Deferred |
| IO-CARD | 2 | Source implemented PR #81; runtime untested | Four news states/return/teardown QA |
| IO-FX-PRIM | 4 | Catalog/research | One move pilot |
| IO-TEX-HGSS | 4 | Catalog/research | One region |
| IO-STATUS | 2 | PRs #82–84 preflight only; Gate C blocked, D open | Runtime graphics headroom and glyphs |
| IO-TEX-RANGER | 5 | Catalog/research | Select material |
| IO-FX-SEQ | 4 | Roadmap only | One multiphase animation |
| IO-NPC-COMP | 5 | Catalog/research | One NPC |
| IO-MODELS | 5 | Catalog/research | Deferred 3D budget |
| IO-PKM-COMP | 5 | Catalog/research | One sprite |
| IO-PKM-REPL | 6 | Roadmap only | Deferred |
| IO-TRN-COMP | 3 | Catalog/research | Ace Trainer pilot |
| IO-TRN-REPL | 6 | Roadmap only | Deferred |

## G7 separately implemented

G7.1–7.7 are source-level CLOSED by docs/visual_overhaul/G7_COMPLETE_SUMMARY.md (PR #60), with owner runtime/visual signoff still outstanding. Merged PRs #50, #53, #55–57, #59 and #60 contain battle UI, menus, window indicators, atmosphere and cohesion modifications. G7.3 risky additions were intentionally deferred. Do not confuse G7 implementation with the 16 later ranked opportunities.

## CI and runtime evidence

GitHub Actions records inspected on 2026-10-09 include successful build runs and repeated failures in g7-visual-validation, while format-visual-overhaul runs pass. These outcomes do not establish the root cause or per-feature ROM revision acceptance. Check historical baseline versus branch before assigning responsibility. No emulator visual signoff was established for IO-PAL-CYCLE or IO-CARD.

## QA matrix

- G7: menus, all message frames, battle HUD in singles/doubles, environment groups, lighting transitions, repeated visits.
- IO-PAL-CYCLE: water platform in singles/doubles, fades, animation interactions, time-of-day, non-water battles, multiple battles and exit cleanup.
- IO-CARD: all four Solaceon articles, input/touch navigation, paging, rewards, re-entry, field return and cleanup.
- IO-STATUS: no sprite allocation until OAM/palette/char VRAM capacity and coordinate tests pass; Gate D native glyph creation outstanding.
- For every test save build commit SHA, ROM revision, emulator/version, precise reproduction steps, screenshots/video and result. Never mark runtime accepted based only on source or CI.

## Next bounded task — IO-PREVIEW

Use docs/visual_overhaul/selection/CROSS_GEN_IMPLEMENTATION_PLAN.md and existing donor provenance. Preflight a single Sinnoh location (Eterna Forest preferred subject to resource suitability): preserve map-name popup, add Platinum-native area preview using HGSS layout techniques and FireRed corroboration. Define hook, graphics formats/palette, memory ownership, time-of-day behavior, lifecycle and acceptance matrix. Code only after static gates pass. No general donor rediscovery.

Evidence: docs/visual_overhaul/implementation/IO_PAL_CYCLE_WATER_PILOT.md; IO_CARD_SOLACEON_IMPLEMENTATION.md; IO_STATUS_COMPOSITE_PREFLIGHT.md; docs/visual_overhaul/G7_COMPLETE_SUMMARY.md; merged PRs #79, #81, #82, #83, #84.
