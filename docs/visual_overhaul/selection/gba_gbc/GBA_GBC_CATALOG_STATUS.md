# GBA/GBC catalog status

| Batch | Donor | Status | Result |
|---|---|---|---|
| B1_emerald_seed_formalization | emerald `a81cfacb…` | complete (PR #72 merged) | 2 reference_only, 1 needs_evidence, 0 promoted |
| B1.5_emerald_env_parity_closure | emerald / platinum fldeff.narc | complete | generic env primitives -> reference_only; Emerald needs-evidence queue = 0 |
| B2_firered_seed_formalization | firered `037335f4…` | complete | 3 seeds -> 4 records (1 subsumed by HGSS area preview, 1 palette technique, 1 split into 2); all reference_only, 0 promoted, 0 needs_evidence |
| B3_pmd_red_status_close | pmd_red `aefe6a46…` | complete | 1 seed -> 3 records: 1 novel_detail, 1 technique_donor (conditional), 1 reference_only; 0 needs_evidence (1 deferred, non-blocking) |
| B4_crystal_primitives | crystal | not started | |
| B5_ruby_semantic_delta | ruby | not started | |
| B6_yellow_high_threshold | yellow | not started | |
| B7_cross_generation_merge | combined | not started | |

Emerald is closed: 3 reference_only records, 0 needs_evidence. B5 (Ruby delta) should reuse `evidence/B1_EMERALD_SYMBOL_EVIDENCE.json` and `evidence/B1_5_PLATINUM_FLDEFF_MEMBER_NAMES.json` instead of re-extracting; any Ruby-only effect that matches a Platinum member already named there is reference_only.

FireRed is closed: 4 reference_only records, 0 needs_evidence. Pool totals: 7 reference_only, every other class 0. FireRed corroborates but does not strengthen `opp:hgss/map_location_preview` (DS pool untouched).

PMD Red status overlay is closed: first non-reference_only dispositions in the GBA/GBC pool. Pool totals: 1 novel_detail, 1 technique_donor, 8 reference_only, every other class 0. B4 (Crystal primitives) is next. The Platinum battle OAM/palette headroom check is deferred and non-blocking.
