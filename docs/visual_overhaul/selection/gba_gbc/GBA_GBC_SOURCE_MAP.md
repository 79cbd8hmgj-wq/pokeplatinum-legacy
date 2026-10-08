# GBA/GBC source map

This source map pins the donor repositories and revisions used for the deferred GBA/GBC visual-mining phase. It is intentionally narrower than a full donor audit: it exists to prevent repeated source-discovery work and to keep later mining deterministic.

## Verified donor repositories

| Donor | Repository | Revision | Initial mining focus |
|---|---|---|---|
| Emerald | `79cbd8hmgj-wq/pokeemerald` | `a81cfacbe53bcc229fc4d93cb10b56a58e77a15f` | field-action choreography, environmental effects, battle-effect sequencing |
| FireRed | `79cbd8hmgj-wq/pokefirered` | `037335f4c725d7c9aecdac87066f2002b4bd7e14` | location previews, palette animation, interactive-object presentation |
| PMD Red | `79cbd8hmgj-wq/pmd-red` | `aefe6a46bcc5df13142225ef673a1ee2ac1b760b` | status overlays, compact feedback/effect primitives |
| Crystal | `79cbd8hmgj-wq/pokecrystal` | `3bc8daa4173e96a7f4011dad3922eb6fa5dad5c6` | battle-animation primitives and choreography |
| Ruby | `79cbd8hmgj-wq/pokeruby` | `5784633ce4ef7ade1a7f2d2d0c288e3d5e6cdd7f` | deltas against Emerald only |
| Yellow | `79cbd8hmgj-wq/pokeyellow` | `e89ead154b9968aa50eed9328ff2b38b6c194382` | selective battle presentation and Pikachu-specific material |

## LeafGreen

No distinct LeafGreen repository was located in the linked repository set during preflight. FireRed remains the shared source/reference base. LeafGreen should only be revisited if a separate source tree becomes available and a unique delta is worth mining.

## Existing project evidence

The current Platinum repository already documents the broad donor roles in:

- `docs/visual_overhaul/PASS_G_VISUAL_OVERHAUL.md`
- `docs/visual_overhaul/CROSS_GAME_DONOR_MATRIX.md`
- `docs/visual_overhaul/G5_DONOR_TECHNIQUE_AUDIT.md`

Nine deferred non-DS findings are preserved in:

- `docs/visual_overhaul/selection/opportunities/deferred/non_ds_findings.json`

Those findings remain seed hypotheses until re-verified at the pinned donor revisions above.

## Mining rule

Prefer source-code/system tracing before broad asset extraction. When readable source identifies a visual system, animation sequence, palette table, event state machine, or referenced graphic family, inspect only the directly relevant assets first.

This reduces context use and avoids spending time on low-value bulk assets.

## Phase boundary

Do not modify the existing DS opportunity pool while collecting GBA/GBC evidence. Verified GBA/GBC findings should remain in a separate layer until the GBA/GBC pool is stable enough for a combined cross-generation ranking.
