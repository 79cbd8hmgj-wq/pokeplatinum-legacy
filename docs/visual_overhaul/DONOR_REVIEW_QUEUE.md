# Donor Asset Cross-Source Review Queue

This queue organizes the donor catalog for review. It does not change
review statuses, select winners, or modify Platinum resources.

## Summary

- Catalog assets covered: **64841**
- Review batch size: **100**
- Review batches: **651**

## Review lanes

| Lane | Assets | Purpose |
|---|---:|---|
| A_render_ready | 40559 | Already has a render path/source PNG; inspect first. |
| B_pokemon_facing | 15157 | Pokémon, trainer, icon, portrait, overworld and battle-facing candidates. |
| C_effects_animation | 1603 | Effects, transitions and animation resources. |
| D_environment_ui | 4724 | Environment, backgrounds, maps, palettes and UI resources. |
| E_decode_or_context_needed | 2798 | Opaque/container/context-heavy candidates requiring more decoding or source interpretation. |

## Assets by source

| Source | Assets |
|---|---:|
| diamond | 7872 |
| hgss | 5784 |
| pmd_sky | 2131 |
| ranger2 | 49054 |

## Batch counts

| Lane | Batches |
|---|---:|
| A_render_ready | 406 |
| B_pokemon_facing | 152 |
| C_effects_animation | 17 |
| D_environment_ui | 48 |
| E_decode_or_context_needed | 28 |

## Review rules

- Review lane assignment is organizational only.
- Existing catalog review status is preserved.
- No donor asset is promoted to usable automatically.
- Replacement/import decisions remain deferred until candidate review is complete.
