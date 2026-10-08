# GBA/GBC catalog status

**FROZEN at B7.** Donor status: Emerald complete, FireRed complete, PMD Red complete, Crystal reviewed (angels motif deferred), Yellow complete, Ruby skipped. Validate with `tools/visual_overhaul/selection/validate_gba_gbc_pool.py`.

| Batch | Donor | Status | Result |
|---|---|---|---|
| B1_emerald_seed_formalization | emerald `a81cfacb…` | complete (PR #72 merged) | 2 reference_only, 1 needs_evidence, 0 promoted |
| B1.5_emerald_env_parity_closure | emerald / platinum fldeff.narc | complete | generic env primitives -> reference_only; Emerald needs-evidence queue = 0 |
| B2_firered_seed_formalization | firered `037335f4…` | complete | 3 seeds -> 4 records (1 subsumed by HGSS area preview, 1 palette technique, 1 split into 2); all reference_only, 0 promoted, 0 needs_evidence |
| B3_pmd_red_status_close | pmd_red `aefe6a46…` | complete | 1 seed -> 3 records: 1 novel_detail, 1 technique_donor (conditional), 1 reference_only; 0 needs_evidence (1 deferred, non-blocking) |
| B4_crystal_primitives | crystal `3bc8daa4…` | complete (combined B4 pass); angels motif deferred | 2 seeds -> 5 records: 3 reference_only, 1 reject, 1 needs_evidence (angels motif); 0 promoted |
| B4_5_crystal_angels_evidence_closure | crystal | **skipped by project decision** | `ne:crystal/angels_motif_vs_platinum` stays open, deferred, non-blocking, excluded from ranking |
| B5_ruby_semantic_delta | ruby | **skipped by project decision** | not mined; deferred, non-blocking |
| B6_yellow_high_threshold | yellow `e89ead15…` | complete (combined B4 pass) | 2 seeds -> 4 records: 3 reference_only, 1 reject; 0 promoted, 0 needs_evidence |
| B7_cross_generation_merge | combined | **complete (final synthesis)** | pool frozen and validated; merged with the DS pool into `../CROSS_GEN_OPPORTUNITY_RANKING.json` and `../CROSS_GEN_IMPLEMENTATION_PLAN.md`; 0 new ranked opportunities, 4 existing ones strengthened |

Emerald is closed: 3 reference_only records, 0 needs_evidence. B5 (Ruby delta) should reuse `evidence/B1_EMERALD_SYMBOL_EVIDENCE.json` and `evidence/B1_5_PLATINUM_FLDEFF_MEMBER_NAMES.json` instead of re-extracting; any Ruby-only effect that matches a Platinum member already named there is reference_only.

FireRed is closed: 4 reference_only records, 0 needs_evidence. Pool totals: 7 reference_only, every other class 0. FireRed corroborates but does not strengthen `opp:hgss/map_location_preview` (DS pool untouched).

PMD Red status overlay is closed: first non-reference_only dispositions in the GBA/GBC pool. Pool totals: 1 novel_detail, 1 technique_donor, 8 reference_only, every other class 0. B4 (Crystal primitives) is next. The Platinum battle OAM/palette headroom check is deferred and non-blocking.

Crystal and Yellow are closed except for one Crystal needs-evidence item (`ne:crystal/angels_motif_vs_platinum`, one five-move key-frame comparison). Pool totals: 1 novel_detail, 1 technique_donor, 14 reference_only, 2 reject, 1 needs_evidence, every other class 0. Neither donor changed the project direction.

Final (B7): the pool is frozen at 19 records (1 novel_detail, 1 technique_donor, 14 reference_only, 2 reject, 1 needs_evidence). Record changes are limited to canonicalising the two PMD Red records' target kinds and cost/risk fields plus `merge`/`deferral` pointers (see `../CROSS_GEN_IMPLEMENTATION_PLAN.md` section 2). The PMD Red overlay merges into the DS record `opp:pmd_sky/battler_status_indicators`; FireRed map preview and palette sequences remain reference_only corroboration. Ruby was not mined and the Crystal angels comparison was not run; neither blocks any ranked opportunity.
