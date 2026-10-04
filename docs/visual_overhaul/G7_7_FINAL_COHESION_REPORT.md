# G7.7 — Final Visual Cohesion Report

Status: **SOURCE-COMPLETE / CI-GATED / OWNER RUNTIME REVIEW PENDING**

Baseline: `main` @ `76f27a81` (merge of PR #59, G7.6). Pinned in
`tools/visual_overhaul/validate_g77_final_cohesion.py` as `G77_BASE`. G7.7 is an integration and
closure pass, not a redesign: no new visual system, no change to approved identity.

## 1. Audit scope and method

Everything merged under G7.1A–G7.6 was reviewed together against the merged tree (not old notes):

| System | Authority | Reviewed via |
|---|---|---|
| G7.1A/B command + move menus | `generate_battle_command_ui.py`, `generate_move_select_palettes.py` | `validate_g7_battle_command_ui.py`, accent audit |
| G7.2A healthboxes | `generate_battle_ui.py` | `validate_g7_battle_hud.py` |
| G7.2B message frames / G7.5 window indicators | `generate_message_frames.py`, `generate_ui_foundation.py` | `validate_g7_message_frames.py`, `validate_g7_global_windows.py` |
| G7.3 encounter intensity | `G7_3_ENCOUNTER_TIER_AUDIT.md` | tier cross-check (§4) |
| G7.4 core menus | `generate_{party_menu,summary,bag,start_menu,shop}_ui.py` | `validate_g7_core_menus.py`, accent audit |
| G7.6 overworld atmosphere | `generate_g76_atmosphere.py` | `validate_g76_atmosphere.py` + new G7.7 audits |

Methods (all scripted, deterministic, read-only unless noted):
* **Lighting:** every lighting set measured against its pinned retail/parent set ("grade strength" =
  mean per-channel distance of key/ambient/diffuse/specular colour, daytime keyframe).
* **Textures:** new read-only NSBTX parser (`nsbtx_palettes.py`; cross-checked against the G7.6
  per-palette report for all 19 graded sets) → per-set Δluma/Δsat/Δwarmth, near-black and
  over-saturation fractions, before/after contact sheets rendered for the Galactic sets.
* **Ownership:** resource → area record → map header table for every graded resource (§6).
* **UI:** focus-accent colours of every menu family compared (§5).
* **Diff:** `git diff` against the PR #59 merge restricted to visual paths (§7).

## 2. Defects found (class A) and exact fixes

| # | Finding | Fix |
|---|---|---|
| A1 | **Hierarchy inversion in lighting.** Natural caves (`lighting_set_015`: Ravaged Path, Oreburgh Mine, Solaceon/Celestic, Stark Mountain, Victory Road, the three lake caverns) were graded as strongly as Distortion World / Turnback (strength 0.58 vs 0.55/0.58), while the legendary Spear Pillar / Hall of Origin set (`lighting_set_012`) was graded only 0.19 — ordinary dungeon content out-competed a legendary space. | `generate_g76_atmosphere.py` (baseline-pinned): cave multipliers roughly halved → strength 0.29; Spear Pillar gets an additional cool/blue-weighted colour grade with near-neutral luma (ambient luma 0.226, floor-guarded ≥ 0.15) → strength 0.61. Outputs regenerated: `lighting_set_012.json`, `lighting_set_015.json` only. Keyframe times/enable flags/directions unchanged (G7.6 validator still passes). |
| A2 | **Tooling defect:** `validate_g7_core_menus.py` reported "generator rerun changed output (not idempotent)" on every checkout honouring `.gitattributes` (`*.pal eol=crlf`; generators write LF) — the check hashed raw bytes. | Hash EOL-normalised content (palette data is identical; verified no real diff). |
| A3 | **Coverage gap:** none of the G7 validators ran in CI (only on developer machines), and the G4 runtime harness did not trigger for G7-only changes. | New workflow `g7-visual-validation.yml` (all G7 validators + generator idempotence, full-history checkout). Lighting changes in this PR also trigger the existing runtime harness. |

No palette/texture/UI image edits were required beyond A1.

## 3. Intentional differences reviewed and preserved (class B)

* **Galactic interiors** (sets 057/067/076): saturation/darkness shift is the largest of any texture group
  (Δsat +0.18…+0.33). Contact sheets show a controlled cyan-accent / cold-neutral grade, not crushed
  darks (the apparent "near-black fraction" is unused/tail palette entries). Veilstone warehouse is a
  bright retail bank (mean luma 0.83) intentionally pulled to the family grade.
* **Distortion World** is the strongest indigo/violet treatment (hue-driven; luma similar to caves by design).
* **Turnback Cave** > natural caves (documented G7.6 ordering), now more clearly so after A1.
* **Start menu cursor orange `(255,106,16)`** and **Summary move-cursor red `(246,74,41)`**: retail accents
  living in palette banks shared with other art (Start bank 1 is also the active-icon palette, 288 icon
  pixels use that entry; Summary sprite bank 1 backs other summary chrome). Both gained G7.4 shape cues
  (brackets/chevron/rim), so selection is not colour-only. Recolouring them would silently change unrelated
  art → preserved; pinned by the G7.7 validator so a future change must be deliberate.
* **Battle cursor `(255,205,48)`** is a brighter battle-state gold of the same hue family as the
  menu gold `(246,172,57)`; accepted.
* Shared-lighting consequences already documented in G7.6 and re-verified in the ownership table:
  Hall of Origin shares the Spear Pillar family (consistent legendary tier); Fullmoon/Newmoon Island
  share the Canalave harbour grade; Lake Acuity/Coronet exterior share the snow grade; Pokémon League
  shares the Sunyshore coast grade.

## 4. Visual intensity hierarchy (measured)

Lighting grade strength (day, lower = closer to retail):

| Tier | Sets | Strength |
|---|---|---|
| Ordinary (coast/lake variants of ordinary-route light) | 017 / 018 / 019 / 013 | 0.13 / 0.26 / 0.10 / 0.23 |
| Standard environments | Galactic 006, Coronet 007/016, Eterna 010, Snow 011, natural caves 015 | 0.19, 0.23/0.23, 0.32, 0.39, 0.29 |
| Special / legendary / boss | Distortion 009, Spear 012, Turnback 014 | 0.58, 0.61, 0.55 |

Ordinary retail sets `000`/`001` and texture sets `000`/`001` are byte-identical to the pinned baseline.
Texture mean |Δluma| of graded sets is 0.012–0.107 (envelope enforced ≤ 0.12), strongest = Turnback.
Hierarchy `ordinary ≤ standard ≤ special` is enforced by the validator (`check_hierarchy`), without
raising global saturation/brightness/contrast anywhere.

## 5. UI readability / cohesion

Existing per-system validators (all pass) cover: command/move label contrast ≥ 3:1, healthbox white-on-fill
≥ 7:1, message-frame and window-indicator contrast ≥ 4.5:1, monotonic command ramps, disabled-slot
distinction. Cross-system findings: Party/Bag/Shop share exactly one gold `(246,172,57)`; Battle cursor is
the same hue family; Start/Summary exceptions pinned (§3). No readability failure found statically.

## 6. Shared-resource decisions

`G7_7_RESOURCE_OWNERSHIP.json` records, for every G7.6-graded lighting set and texture set, the consuming
area records **and map headers** (with map type/label). The validator regenerates the table and fails on
any new/removed consumer, any graded resource with no consumer, or a Pokémon Center consuming a graded set.
A1 touched only dedicated lighting sets (`012`: area 060 only; `015`: five cave area records only) — no
shared retail resource was modified.

## 7. Guards and validation

| Check | Result |
|---|---|
| `validate_g77_final_cohesion.py` (diff guard, ownership, texture envelope, hierarchy, UI accents, ordinary sets untouched) | PASS; negative tests confirmed it fails when A1 is reverted and when `src/main.c` is touched |
| `validate_g76_atmosphere.py` | PASS (19 sets/398 palettes palette-only; 13 lighting sets structure-preserving; 11 area records lightingSet-only) |
| `validate_area_light_contract.py`, `validate_g6_showcase_integration.py` | PASS |
| `validate_g7_battle_command_ui/battle_hud/core_menus/global_windows/message_frames` | PASS |
| `generate_g76_atmosphere.py` second run | byte-identical (baseline `896570704f26`) |
| `validate_overhaul.py --no-write` | see PR (run locally; all suites PASS) |
| `validate_g4*` recolour validators | N/A — compare transient CI dump dirs that no longer exist (pre-existing, unchanged) |
| US Rev 0 build / US Rev 1 build / runtime harness (both revisions) | **recorded in the PR after CI** (`build`, `g4-runtime-harness` debug-symbol gate ×2) |

Non-visual diff vs PR #59: none (gameplay guard is part of the validator and CI).

## 8. Manual QA checklist (owner, portrait stacked and landscape)

| Scene | Confirm |
|---|---|
| Ordinary outdoor route (e.g. Route 201/202) | Unchanged from G7.6 look; still the calmest outdoor reference. |
| Town/city (Jubilife/Sunyshore) | Sunyshore warm sand/turquoise reads as resort, Jubilife unchanged; text overlays legible. |
| Interior (houses, Pokémon Center, Galactic HQ) | Ordinary interiors untouched; Galactic reads cold/cyan but wall vs floor is separable. |
| Cave (Oreburgh Mine, Ravaged Path, Victory Road) | **New softer grade**: darker/cooler than a route but clearly less oppressive than Turnback; floor/wall separation, ladders, exits. |
| Dungeon/special (Turnback, Distortion) | Strongest, most oppressive grading; navigation intact. |
| Spear Pillar / Hall of Origin | **New stronger cool grade**: hard cool light, shade not crushed; Dialga/Palkia/Arceus scenes legible; clearly more dramatic than Eterna/Snowpoint. |
| Ordinary trainer battle / wild battle | Command menu, healthboxes and messages legible on light and dark battle backgrounds; no accidental tint. |
| Important trainer/boss battle | Presentation still stands above ordinary battle (G7.3 tiers). |
| Legendary encounter | Legendary > boss > ordinary in intensity. |
| Battle command menu / move menu | Selected vs unselected, disabled/empty slot, PP colours legible. |
| Healthboxes | HP bar states, status icons, player vs opponent legibility. |
| Battle messages / dialogue boxes / indicators | All 20 frames: text and scroll/wait indicator contrast. |
| Menus (Start, Party, Summary, Bag, Shop) | Gold focus consistent in Party/Bag/Shop; Start orange and Summary red are the preserved retail accents (§3) — owner may rule on aligning them (would need new palette entries/art). |
| Transitions between graded areas | Route→snow, Route→coast/lakes, cave entrance↔exterior, Coronet 3F↔4F, Spear Pillar approach: no jarring discontinuity beyond the intended family boundary. |
