# Special Acquisition — closure of the 28 deferred families

Baseline: `main` @ `f89dfc79` (ordinary availability, PR #10). Scope: the **28 nonlegendary families** that PR #10 reserved as
`USER_DECISION_REQUIRED`. Status: **IMPLEMENTED; source + build + validator verified; runtime QA pending.**
Machine-readable authority: `special_acquisitions.json` (verified by `tools/overhaul/availability/special_verify.py`).
The 184 wild-placed families, all encounter JSON, and every species/move/trainer/TM/evolution file are unchanged
(`special_scope_audit.py`).

## Recovered ledger (exact deferred set = 28)

`availability_families.json` at `f89dfc79` listed 28 families with `user_decision_required: true`:
12 starters, 7 fossils, Spiritomb, Rotom, Tyrogue, Happiny/Chansey, Eevee, Porygon, Riolu, Castform, Feebas.

| Family | Vanilla / source acquisition | Why deferred | Overhaul path (this pass) | Files | Engine/script change |
|---|---|---|---|---|---|
| Turtwig, Chimchar, Piplup | Route 201 choose-one-of-three (`scripts_route_201.s`, `StartChooseStarterScene`) | two of three unobtainable | Sandgem Lab research assistant gifts the two unchosen at **2 badges** (Lv 15) | `scripts_sandgem_town_pokemon_research_lab.s`, text bank | script + text + flags |
| Bulbasaur, Charmander, Squirtle | none (Slot-2/trade only) | external-only | same NPC, **3 badges** (Lv 20), one gift per visit | same | script |
| Chikorita, Cyndaquil, Totodile | none | external-only | same NPC, **4 badges** (Lv 25) | same | script |
| Treecko, Torchic, Mudkip | none | external-only | same NPC, **5 badges** (Lv 28) | same | script |
| Omanyte, Kabuto, Aerodactyl, Lileep, Anorith | Underground mining (`src/underground/mining.c`) | weight 0 before the National Dex; fossil weights differ by Trainer ID parity | one Trainer-ID- and Dex-independent weight per fossil (12 per family); revival at the Oreburgh Mining Museum unchanged | `mining.c` | source (data) |
| Shieldon, Cranidos | Underground mining | weight 0 for odd (Armor) / even (Skull) Trainer IDs | same | `mining.c` | source (data) |
| Spiritomb | Odd Keystone + Hallowed Tower after **32 Underground player conversations** (`underground/player.c`); an uncaught Spiritomb ends the ritual | multiplayer; no retry | Odd Keystone = existing Twinleaf hidden item (deterministic); the tower counter rises by 1 per **object unearthed in Underground mining** (single player); an uncaught Spiritomb leaves the ritual intact | `mining.c`, `scripts_route_209.s`, text | source + script |
| Rotom | Old Chateau TV static, night only, **once per day**; appliance room needs a Mystery Gift Secret Key | daily cap, WFC gate on forms | static kept (night); daily cap removed (retry until caught); the capture grants the Secret Key and the form-room unlock value; appliance system untouched | `scripts_old_chateau_back_middle_west_room.s`, text | script |
| Tyrogue | breeding only (Radar slot, Route 211 W) | no early path | Celestic Town Black Belt (fighting-themed) gifts Lv 15 Tyrogue after his Poketch-watch gift | `scripts_celestic_town_southwest_house.s`, text | script |
| Happiny / Chansey | Chansey 1 %/4 % Routes 209/210 (kept as bonus), Trophy Garden daily | no deterministic Happiny | same Black Belt gifts Lv 10 Happiny after Tyrogue (the Happiny in his room) | same | script |
| Eevee | Hearthome NW house gift (Lv 20) | validator only counted wild | **unchanged**; verified: party-full guard, flag after give, Hearthome = 3rd gym town | `scripts_hearthome_city_northwest_house.s` | none |
| Porygon | Veilstone NE house gift (Lv 25) | same | **unchanged**; verified retry-safe | `scripts_veilstone_city_northeast_house.s` | none |
| Riolu | Riley's egg, Iron Island B2F | same | **unchanged**; verified: full party sets `FLAG_COULD_NOT_RECEIVE_RIOLU_EGG`, Riley re-offers, success clears it | `scripts_iron_island_b2f_left_room.s` | none |
| Castform | Trophy Garden daily only | rotation-only | Veilstone City parasol woman (weather-report watcher) gifts Lv 22 Castform | `scripts_veilstone_city.s`, text | script |
| Feebas | Mt. Coronet B1F, 4 tiles re-rolled from the mixed-record RNG | random-tile lottery | **4 fixed tiles** (below), same 50 % hit chance, any rod | `src/overlay006/feebas_fishing.c` | source |

No family was converted into a generic wild encounter; Eevee/Porygon/Riolu needed no change.

## Rules implemented

* **Starters.** Gifts are offered one per visit (yes/no), skip the player's chosen Sinnoh starter, require a free party slot
  before the flag is set, and each starter has its own flag (`FLAG_RECEIVED_STARTER_<REGION>_<SPECIES>`, 12 flags in
  `generated/vars_flags.txt`, formerly unused slots). No gift consumes anything; no choice locks another family.
* **Fossils.** Weights per object: Helix 3×4 rotations, Dome 12, Claw 3×4, Root 3×4, Old Amber 6×2, Armor 12, Skull 12 — all four
  weight fields equal (odd/even Trainer ID, with/without National Dex). The Underground still starts with the Eterna Explorer Kit.
* **Spiritomb.** The 8/15/22/29/32 hint thresholds in `scripts_route_209.s` are unchanged; with 2-4 objects per dig the ritual needs
  roughly 11 digs. The counter is capped at 999 and still also rises from the original multiplayer path.
* **Rotom.** Night requirement kept (identity); retries unlimited until caught. Capture runs
  `SetVar VAR_DISTRIBUTION_EVENT_ROTOM, 0x1103` + gives `ITEM_SECRET_KEY`, which satisfies the existing
  `CheckDistributionEvent` gates in the Eterna Galactic building and Rotom's room, so no appliance script was rewritten. This is
  compatible with `events/LEGENDARY_MYTHICAL_EVENT_SPEC.md` s.5 (the event-restoration phase may later delete the check outright).
* **Feebas.** `FEEBAS_FIXED_TILE_SEED = 0x42424242` selects, per quarter of the 528-tile lake, tile index `132·i + 66`:
  (x,z) = **(23,21), (12,29), (21,39), (12,48)** in map-matrix tile coordinates (same space as `elusive_rod_encounter.tiles`).
  Mt. Coronet B1F is banded P0 (Waterfall route); Feebas is still pre-E4.

## Validator coverage (S-codes, `special_verify.py`)

S1 path present in source · S2 retry-safe (party guard before give, flag only after give, failure recovery, uncaught-static
retry) · S3 gate/band ≤ PRE_E4 · S4 no external dependency (trade, link/multiplayer, Wi-Fi, Mystery Gift/distribution,
National Dex, day-of-week/daily flags, random, Trainer ID, random Feebas tiles) · S5 no mutually exclusive one-time choice.
`test_validators.py`: the 12 original mutation cases still pass, plus 25 special-acquisition cases and a vanilla-source control
(the pre-pass source is rejected for fossils, Spiritomb, Feebas, Rotom, Castform, Tyrogue, Happiny and the starters).

## Known limits / not claimed

* Runtime QA (gift scenes, full-party retry, mining odds, Spiritomb battle, Rotom TV/form room, Feebas bites, starter flow) is **pending**.
* Gift levels, badge thresholds and the fossil weight totals are tuning choices, easy to adjust in `special_acquisitions.json` + source.
* Trophy Garden Castform/Eevee/Happiny dailies and the Chansey wild slots were left as pure bonus sources.
* Pseudo-legendary secondary habitats and the National Dex UI timing remain undecided (not part of this pass).
