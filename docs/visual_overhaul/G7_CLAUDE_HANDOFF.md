# G7 — Claude Code Handoff

Use this file together with:
- `docs/visual_overhaul/G7_CLAUDE_EXECUTION_PROTOCOL.md` — operational/session rules
- `docs/visual_overhaul/G7_MODERN_DS_REMASTER_DESIGN.md` — design authority
- `docs/visual_overhaul/G7_MODERN_DS_REMASTER_IMPLEMENTATION_PLAN.md` — implementation authority

## Execution mandate

Implement G7 as an escalation of the existing Pass G visual overhaul. Do not redesign from memory and do not restart from retail Platinum assets.

The user has already approved the G7 direction:
- modern DS remaster;
- designed for DS emulation on iPhone;
- dual-screen/touch semantics preserved;
- more immersive and intense;
- willing to stray from retail Platinum authenticity;
- runtime visual approval will be handled by the user.

## Required workflow

1. Start from current `main`.
2. Create/use `visual/g7-modern-ds-remaster`.
3. Read `G7_CLAUDE_EXECUTION_PROTOCOL.md` first and obey its bounded-session rules.
4. Read the design document and only the implementation-plan section relevant to the current numbered section, expanding context only when necessary.
5. Audit exact resource/code ownership for all subparts of the current section using targeted search.
6. Preserve all gameplay and input semantics.
7. Prefer deterministic generator-backed assets.
8. Complete all subparts in the current numbered section before final validation.
9. Validate and build once at the end of the numbered section.
10. Commit/document the section, then **stop before the next numbered G7 section**.

## Current target

G7.1–G7.2 are implemented. G7.3 was audited and intentionally deferred for runtime-sensitive battle-impact additions. G7.4 core menus and G7.5 global windows are implemented and merged.

**Current implementation section: G7.6 — Overworld Atmosphere Escalation.**

Complete all of G7.6 in one Claude session.

Priority environments:
1. Eterna / deep forest
2. Route 217 / Snowpoint
3. Galactic interiors
4. Mt. Coronet / Spear Pillar
5. Distortion World
6. lakes / coastal routes
7. caves / Turnback Cave

Use the existing G4/G6 environment work as the foundation. Do not restart from retail assets and do not blindly recolor shared resources.

Primary prior records:
- `docs/visual_overhaul/G4_ENVIRONMENT_RECONSTRUCTION_COMPLETE.md`
- `docs/visual_overhaul/G4A_ETERNA_FOREST.md`
- `docs/visual_overhaul/G4B_SNOW_ENVIRONMENT.md`
- `docs/visual_overhaul/G4C_DISTORTION_WORLD.md`
- `docs/visual_overhaul/G4D_G4F_SHOWCASE_ENVIRONMENTS.md`
- `docs/visual_overhaul/G4G_GALACTIC_INTERIORS.md`
- `docs/visual_overhaul/G6_SHOWCASE_INTEGRATION_COMPLETE.md`

Primary tools/contracts:
- `tools/visual_overhaul/apply_g4_showcase_passes.py`
- the existing `recolor_g4*.c` tools
- the existing `validate_g4*.py` validators
- `tools/visual_overhaul/validate_area_light_contract.py`
- `src/overlay005/area_light.c`
- `src/overlay005/fieldmap.c`
- `res/field/lighting/`
- `res/field/area_data/`

Goals:
- deepen authored atmosphere and regional identity;
- preserve player/NPC silhouette readability;
- preserve terrain/collision/navigation clarity;
- keep weather/fog coherent;
- avoid accidental cross-map-family grade leakage;
- use selective dedicated resource slots only when shared retail resources would otherwise cause collateral changes.

Allowed:
- stronger palette separation;
- safe fog tuning;
- reuse of proven existing field effects;
- small atmosphere emitters through already-proven resource paths;
- dedicated resource isolation where the current G4/G6 pipeline supports it.

Do not:
- replace whole map texture families blindly;
- churn geometry;
- change collision;
- alter scripts/gameplay for aesthetics;
- perform opaque NARC patching without a verified pipeline;
- make navigation harder;
- begin G7.7.

If one environment has a genuine isolation blocker, document that environment precisely, continue the other G7.6 environments, and stop the whole section only for a section-wide blocker.

## Validation

At the end of the full G7.6 section:
- all relevant existing G4/G6 environment validators;
- area-light contract validator;
- rerun every touched deterministic generator/recolor/apply step and confirm reproducibility;
- core master validator if shared code/resource plumbing changed;
- US Rev 0 build;
- US Rev 1 build;
- concise G7.6 implementation report covering all seven priority environment groups;
- clean git status.

Then stop before G7.7.
