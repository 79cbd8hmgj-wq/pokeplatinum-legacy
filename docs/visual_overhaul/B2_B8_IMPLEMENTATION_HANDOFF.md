# B2–B8 production handoff — decisions prepared outside Claude Code

Read `B2_B8_PREIMPLEMENTATION_MANIFEST.json` first. It fixes the implementation direction without making unsupported asset-compatibility claims. This file contains **design decisions and acceptance criteria**, not a claim that the systems have been implemented.

## Decision rules
1. Continue **PR #110**; never touch PR #109.
2. Finish buildable source batches autonomously; ROM rev0 and rev1 through CI. User handles runtime checks.
3. Preserve battle logic, existing G7 HUD and S2-D palette/terrain owners, VRAM/OAM constraints, singles/doubles and contest variants.
4. All six treatments remain available: preserve/reuse, recolor, donor adaptation, composite, nonnative conversion, new rendering code. No blanket exclusion for complexity.
5. Use verified installed Ranger sprites before new extraction. For uninstalled candidates, record **exact recovered donor identifiers** and inspect rendered asset first. The source catalog's **usable** status alone does not mean binary compatibility.

## Already integrated — don't rebuild
- `ranger_fire_bloom` (e010; eight frames; 236 OBJ tiles): Fire group
- `ranger_ice_bloom` (e009; eight frames; 236 OBJ tiles): Ice group
- `ranger_rock_burst` (e002; nine frames; 219 OBJ tiles): Rock group

Their authoritative frame hashes, palettes and donor package metadata are under `docs/visual_overhaul/b1_installed_donors/`. Existing converters and recipes are in `tools/visual_overhaul/`. Avoid re-extracting them during every run.

## B2 first execution group

| Target | Visual treatment | Implementation constraints |
|---|---|---|
| Thunderbolt | Lightning discharge with charge, layered branching impact and dissipating electrical arc | Maintain fade/light restoration; reuse native `thunderbolt_spa` unless a proven converted graphic exists |
| Shadow Ball | Charge and travel with darkened arena, spectral bloom and aftertrail | Preserve background fade, emitter lifecycle, defender targeting |
| Surf | Sweeping water-field surge with layered spray and multi-target hits | Maintain existing friendly-fire and doubles behavior, cleanup on every branch |
| Fire/Ice/Rock families | Retiming and richer compositing using the three *already installed* Ranger sprites | Preserve donor provenance and per-asset OBJ tile budgets |

Do not force the same donor sprite onto visually unrelated moves. An effect requires demonstrated visual appropriateness and resource compatibility.

## Camera, lighting and reactions — design contracts for B3–B5

- **Camera:** animation-local effect rather than global engine takeover; start -> action -> settle -> restore. Favor BG scroll, transforms and sprite movement already in source; introduce C capabilities only when necessary. Never displace a healthbox or corrupt a battler's logical position.
- **Lighting:** composited palette/fade transitions must respect existing S2-D terrain cycles and fade ownership. No persistent palette writes beyond an animation's lifecycle.
- **Reactions:** directional recoil, anticipation, return-to-idle; after every route ensure sprite locations and priorities return to their previous values. Doubles and faint interrupts require safe fallback.
- **Durations:** short common actions, longer powerful/legendary actions; derive timing from existing animation tasks rather than hard-coded total-frame assumptions. The owner checks subjective pacing later.

## Sequence patterns for B6

Projectile, beam, area, contact, status and encounter archetypes have explicit phases in the JSON manifest. Reuse a common sequence where it reduces duplicated code **without** imposing a single generic visual on unrelated elements. Sound synchronization must not change mechanics.

## B7 and B8

- Special encounters: constrain enhancements to presentation hooks and existing encounter identifiers. Defer uncertain hooks rather than alter event logic.
- Cohesion: preserve Opal pearl/mineral-violet/controlled-gold identity for framing/UI, while allowing elemental move color. Document exact source assets imported, resource IDs, archive order and budget; run validators and both ROM revisions.

## Evidence tiers (never conflate them)

1. **designed**: recipe/manifest only
2. **source-installed**: C, assembly, graphics, and build manifest wired in repository
3. **source-validated**: static checks pass
4. **build-verified**: both rev0/rev1 ROM artifacts uploaded
5. **runtime-accepted**: owner confirms actual on-screen behavior

A design recipe does not satisfy a phase implementation criterion. A successful build does not imply stage 5.

## Claude token-efficient usage

Read this handoff + machine manifest + affected source files. Do **not** repeat whole-catalog discovery, prior audits, or copy these specifications into additional reports. Batch related moves and CI tests. Keep one short checkpoint recording file paths, phase and known blockers.
