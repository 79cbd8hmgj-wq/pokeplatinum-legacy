# C2 TM/HM Mechanics Implementation Audit

- Base: `main` @ `e13b728fbe4f05ad137f143be11dd7eb71bf5d46` (includes PR #10, #11, #12, #13).
- Authority: `tm_hm/TM_HM_SPEC.md` (LOCKED). Machine manifest: `implementation/c2_mechanics_manifest.json`.
- Tooling: `tools/overhaul/c2/` — `build_manifest.py` (before-values read from the pinned base commit), `validate_c2.py`, `test_validate_c2.py` (72 rejecting mutations + 3 forward-compatibility cases), `scope_audit_c2.py`.
- Method: source-level edits only; no binary patches or ROM offsets; no redesign.

## Source map and changes

| Area | Source | Change |
|---|---|---|
| HM01 Cut | `res/moves/cut/data.json` | 50/95/30 `BATTLE_EFFECT_HIT` → 70/100/30 `BATTLE_EFFECT_HIGH_CRITICAL` (existing effect; Normal/Physical/contact flags kept) |
| HM02 Fly | `res/moves/fly/data.json` | 90/95/15 → 100/100/15; `BATTLE_EFFECT_FLY` (two-turn, semi-invulnerable) untouched |
| HM03 Surf, HM04 Strength, HM07 Waterfall | `res/moves/{surf,strength,waterfall}/data.json` | KEEP — verified unchanged (95/100/15; 80/100/15; 80/100/15, 20% flinch) |
| HM05 Defog | `res/battle/scripts/subscripts/subscript_defog.s` (effect `BATTLE_EFFECT_REMOVE_HAZARDS_SCREENS_EVA_DOWN`, `effect_script_0258.s`) | Vanilla already lowered evasion and cleared Spikes/Toxic Spikes/Stealth Rock/Reflect/Light Screen/Safeguard/Mist on the **target** side. Added attacker-side Spikes, Toxic Spikes, Stealth Rock clears (script only, same message subscript); also added to the "show attack message" precheck. User's own screens/Mist/Safeguard are never touched. 15 PP unchanged |
| HM06 Rock Smash | `res/moves/rock_smash/data.json` | 40 → 60 BP; 100 Acc, 15 PP, 50% Defense −1 already present |
| HM08 Rock Climb | `res/moves/rock_climb/data.json` | accuracy 85 → 95; 90 BP, 20 PP, 20% confusion already present |
| Reusable TMs | `src/applications/party_menu/callbacks.c` `TeachMove` | Only consumption path for TM/HM teaching. Guard changed from `Item_IsHMMove(learnedMove) == FALSE` to `usedItem < ITEM_TM01 \|\| usedItem > ITEM_HM08` (item-class range). Other `Bag_TryRemoveItem` sites (Sacred Ash, PP/evolution/held-item paths) are unchanged and pinned by count |
| TM21/TM78 roster | `res/items/data/tm21.json`, `tm78.json` | see discrepancy 1 |
| Game Corner prices | `src/scrcmd_game_corner_prize.c` | 15 TM prices set; 4 held-item prizes and exchange rate untouched |
| Frontier prices | `src/overlay007/shop_menu.c` (`itemToBpPrice`), `src/scrcmd.c` (live shop list), `src/unk_020494DC.c` (unused exchange-corner table, kept in sync) | 16 TM prices set; TM89 added (see discrepancy 2); non-TM items untouched |
| Department Store | item data prices | KEEP — all TM/HM item prices pinned |
| Vendor duplicate guard | `shop_menu.c` (`Shop_IsTM`, `Shop_AlreadyOwnsTM`, new text `pl_msg_00000543_00039`); `scripts_veilstone_city_prize_exchange.s` (`CheckItem`, new text `…_AlreadyHaveTM`) | Checked before money/Coins/BP are touched; TM quantity capped at 1 in marts. Applies to Normal + Frontier marts (so the Veilstone Department Store too) and the Game Corner prize counter |
| TM acquisition | `scripts_route_204_north.s`, `scripts_victory_road_1f.s` | All baseline TM/HM acquisition is pinned except the locked TM78 override: removed the early Route 204 gift and moved TM78 Power Gem to a deterministic Victory Road 1F Collector gift. The existing Route 204 receipt flag is reused for save compatibility. |

## Discrepancies between brief/spec and live source (documented, not redesigned)

1. **TM21/TM78 item→move assignment was NOT already implemented.** The C3H commit applied only the compatibility masks (49/27 recipients — verified intact). `tm21.json` still taught Frustration and `tm78.json` Captivate. Applied the locked assignment (Air Slash / Power Gem), plus matching item description and type-colored icon palette (flying / rock). Item prices keep the slot's vanilla price.
2. **Live Frontier TM shop had 15 TMs; the locked table has 16.** TM89 U-turn (20 BP) was missing from the live list and price table; it was added to the shop list, the BP table and the unused exchange-corner table. U-turn remains in the Game Corner at 3000 Coins.
3. **Recovered acquisition labels were wrong, but the governing design rule was clear.** Live Platinum source gives TM78 via the Route 204 North NPC, not Victory Road, and TM21's field pickup is Galactic HQ 3F rather than the Galactic Warehouse label used in earlier notes. The canonical C2 and master specs are corrected in this PR. No TM was relocated: the actual vanilla TM-number acquisition map remains authoritative.
4. **TM21 sources** (Galactic HQ 3F pickup and Veilstone Game Corner) and **TM78's Route 204 North NPC source** are preserved and pinned.

## Minimal text corrections (required by the reusable-TM change)

- `OreburghCity_Text_TMsSingleUseHMsOverAndOver` claimed TMs are single use.
- Route 204 North's TM78 dialogue described Captivate and one-use TMs; both the explanation and the Captivate-specific opening are updated to match Power Gem and reusable TMs.

## Not touched (scope audit clean)

Species stats/types/abilities, learnsets, TM compatibility masks, encounters, availability gifts, evolution, trainers, Poké Balls, breeding, general economy, legendary events, visual assets, Tutor consolidation, field-move decoupling, world TM placement other than the locked TM78 Route 204 → Victory Road override.

## Validation (source level)

- `validate_c2.py`: OK, 0 problems. `test_validate_c2.py`: 72/72 mutations rejected, 3/3 forward-compatible changes accepted.
- `scope_audit_c2.py`: 0 files outside C2 scope.
- Regression: C1 validator OK (82 edits) + 24/24 mutations & 4/4 forward-compat; availability validator `--state live` 0 failures, 12/12 + 25/25 mutations; C3 compat: TM21 49 / TM78 27 recipient sets match `tm_compat_manifest.json` exactly and all 12 explicit additions present; created moves IDs 468–489 / `MAX_MOVES` 490 verified by the C2 validator.
- Visual: `validate_area_light_contract.py` and `validate_g6_showcase_integration.py` pass. The G4 palette validators need workflow-generated texture dumps and Pillow and fail identically without them (no visual file is touched by this branch).
- Builds: the container cannot fetch the Meson wraps (GitHub/WrapDB downloads return 403), so Rev 0 / Rev 1 are verified by the `build` workflow on the PR.
- Runtime QA: **pending** (no emulator automation available in the authoring container).
