# Pokémon Opal — Visual Slice 01: Ace Trainer Composite Enhancement

Status: **design / bounded implementation handoff; original battle sprites not modified in this commit**.
Associated with Pokémon Opal's creative donor policy and the existing `CROSS_DONOR_IMPLEMENTATION_PLAN.md` S1. This is **not** an HGSS import or a complete global art redesign.

## Why this slice now

The existing hand-ranked `IMPLEMENTATION_SLICE_RANKING.json` puts S1 (HGSS-derived shading components for Ace Trainer M/F) at rank 1 with score 41, cost S and low technical risk, followed by S2 PMD Sky-inspired battle terrain palette cycling and S3 Ranger 2-inspired news presentation. This is an already-researched composite opportunity, not a new bulk donor search. Use the ranking as a planning baseline, not a claim of implementation approval.

## Exact host and donor evidence

| Role | Path or reference |
|---|---|
| Opal host (male) | `res/trainers/classes/ace_trainer_male/front.png` |
| Opal host (female) | `res/trainers/classes/ace_trainer_female/front.png` |
| Cell metadata — preserve | `res/trainers/classes/ace_trainer_male/front_cell.json` and `res/trainers/classes/ace_trainer_female/front_cell.json` |
| HGSS components | `hgss_trainer_sprites` extension, `front_024` male, `front_025` female |
| Source recipe | `docs/visual_overhaul/selection/CROSS_DONOR_IMPLEMENTATION_PLAN.md` S1 |
| Existing evidence | `docs/visual_overhaul/selection/synthesis/track_a_ace_trainer_comparison.png` |
| Mockup measurement | `docs/visual_overhaul/selection/synthesis/mockup_stats.json` |

Both original cell resources inspected in source specify one cell with 16-colour OAM components; no cell/animation format change is called for.

## Authoring recipe

**Male:** retain Opal/Platinum trainer silhouette and outfit/pose. Reauthor the torso seam, zip/hem highlights and 3-tone fold shading using the existing local brown ramps; redraw selected glove highlights in the existing palette. HGSS is a structural/shading reference, not a request for a whole sprite swap.

**Female:** retain body/hair silhouette, pose and original hair form. Refine existing green hair highlight clusters and local collar/zip/hem shading without importing HGSS garments, boots or costume outline.

**Constraints:**
- Do not copy full HGSS sprites or shift Opal into HGSS's visual identity by default.
- 80×80 indexed front sprite, 4bpp/16-colour palette, index 0 transparent, existing palette entries and OAM/cell/animation descriptors unchanged.
- Distinguish untouched native pixels, altered native pixels, direct donor material (target **0**), and newly authored derived pixels in comparison evidence.
- Original simulation changed 31/1205 male opaque pixels (2.6%) and 92/1230 female opaque pixels (7.5%); these are **mockup statistics**, not mandatory targets or finished art.
- Do not touch battle engine, trainer class ID tables, unrelated `res/` assets, or the 572-sheet follower catalog.

## Implementation boundary

1. Construct the two final hand-authored variants on a temporary working branch/asset copy.
2. Generate 1× and 4× side-by-side comparisons against unmodified host sprites, with indexed palette and silhouette checks.
3. Review each donor-derived feature independently (male torso folds, gloves; female hair, seam/collar). Reject any change that harms clarity, pose or visual cohesion.
4. Only after the final art is approved, use the existing guarded pixel patch utility (`tools/visual_overhaul/selection/apply_platinum_sprite_pixel_patch.py` if present at the implementation ref; verify exact CLI) with before hashes.
5. Build the supported Platinum revisions; test Ace Trainer class battle intros in emulator, including sprite animation and backgrounds.
6. Record screenshots, source provenance, reviewer decisions, source commit, build results, and rollback instructions in the implementation PR. If it looks worse in game, preserve the native Opal/Platinum host.

**Definition of done:** two reviewed, integrated, visually better battle sprites with unchanged technical contracts, successful build, and in-battle comparison. A design note or static mockup is not completion.

## Next slices (not automatically approved for runtime implementation)

- **S2:** PMD Sky palette/tile-cycle *technique* as a subtle animated battle-terrain treatment; verify runtime palette ownership/VRAM and flicker risk before edits.
- **S3:** Ranger 2-inspired newspaper-card composition; needs visual direction and BG/window lifecycle spike before a script/runtime implementation.
- **S4:** new area previews may reuse S3 host after it is proven, with original Opal artwork rather than wholesale imported cards.

## Portfolio rule

IO-FOL-SHEETS remains a 572-sheet **donor catalog/exporter**, not an implementation target. Opal work prioritizes **individual assets and composites by game-visible value**. No mass follower ID registration or resource packaging is required for this slice.
