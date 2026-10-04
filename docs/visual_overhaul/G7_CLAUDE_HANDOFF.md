# G7 — Claude Code Handoff

Use this file together with:
- `docs/visual_overhaul/G7_MODERN_DS_REMASTER_DESIGN.md`
- `docs/visual_overhaul/G7_MODERN_DS_REMASTER_IMPLEMENTATION_PLAN.md`

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
3. Read the G7 design and implementation plan completely before editing.
4. Audit the exact resource/code ownership of the first target.
5. Implement **G7.1A battle command menu** first.
6. Preserve all gameplay and input semantics.
7. Prefer deterministic generator-backed assets.
8. Validate/build before advancing.
9. Continue through the plan without asking for routine approval.
10. Stop only for a real blocker listed in the implementation plan.

## First target

Trace and redesign the current Fight / Bag / Pokémon / Run command interface.

The desired result:
- keeps the large touch-friendly surfaces visible in the current build;
- uses stronger hierarchy and more deliberate composition;
- Fight remains dominant;
- secondary actions remain obvious;
- selected/pressed state is unmistakable without color alone;
- less empty filler;
- cleaner depth and panel treatment;
- native 256×192 readability;
- correct in portrait stacked and landscape side-by-side emulator layouts.

Do not assume the visible panels are all sprites; trace whether they are BG tilemaps, windows, sprites, or mixed.

## Validation

At minimum after the first batch:
- relevant visual validators;
- generator rerun produces no diff;
- core master validator if integration touches shared code/resource plumbing;
- US Rev 0 build;
- US Rev 1 build.

Commit the first batch separately and record what changed before moving to G7.1B.
