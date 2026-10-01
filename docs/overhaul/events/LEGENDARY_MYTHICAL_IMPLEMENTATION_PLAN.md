# Pokémon Platinum Overhaul — Legendary/Mythical Implementation Plan

Status: **LOCKED IMPLEMENTATION PLAN**

Authority:
- `docs/overhaul/events/LEGENDARY_MYTHICAL_EVENT_SPEC.md`
- `docs/overhaul/AVAILABILITY_ARCHITECTURE.md`
- locked D3 Poké Ball and D4 Breeding specs

Claude Code implements; it must not redesign acquisition treatment.

## 1. Source audit

Inventory exact scripts, flags, vars, objects, items, encounter tables, and retry behavior for:
- Uxie / Mesprit / Azelf;
- Giratina / Turnback Cave;
- Dialga / Palkia;
- Heatran;
- Cresselia / Lunar Wing;
- Regigigas;
- Darkrai / Member Card / Newmoon Island;
- Shaymin / Oak's Letter / Seabreak Path / Flower Paradise;
- Arceus / Azure Flute / Hall of Origin;
- Rotom / Secret Key / appliance room;
- Regirock / Regice / Registeel ruins;
- Articuno / Zapdos / Moltres roaming;
- Manaphy Egg support;
- Deoxys meteorite form system;
- postgame encounter tables used by the locked legacy habitats.

Do not perform broad unrelated reverse engineering.

## 2. Manifests

Create:
- `docs/overhaul/implementation/events/native_legendary_events.json`
- `docs/overhaul/implementation/events/legacy_legendary_encounters.json`
- `docs/overhaul/implementation/events/mythical_statics.json`
- `docs/overhaul/implementation/events/event_gate_removals.json`
- `docs/overhaul/implementation/events/event_retry_rules.json`

Required fields:
- species;
- acquisition class;
- map/system;
- level/rate;
- vanilla gates;
- target gates;
- one-time vs renewable;
- capture flag;
- retry behavior;
- external dependency removed;
- source path;
- validation status.

## 3. Validator

Create:
`tools/overhaul/validate_legendary_availability.py`

It must fail if any Legendary/Mythical through #493:
- has no in-save path;
- still depends on distribution, WFC, migration, Slot-2, another version/game/system, multiplayer, or trading;
- has a one-time encounter that can be permanently lost without capture;
- has conflicting acquisition ownership;
- violates the locked Hall-of-Fame gate for legacy rare habitats.

Generate:
`docs/overhaul/implementation/events/LEGENDARY_EVENT_VALIDATION_REPORT.md`

## 4. Native Sinnoh retry safety

Normalize:
- Uxie;
- Azelf;
- Mesprit;
- Giratina;
- Dialga;
- Palkia;
- Heatran;
- Cresselia;
- Regigigas.

Rules:
- caught flags set only after confirmed capture;
- defeat/flee/blackout does not permanently consume an uncaught encounter;
- defeated roamers receive a deterministic reset path;
- preserve story order and existing presentation.

## 5. Darkrai

Reuse Harbor Inn/Newmoon Island.

Implement:
- Hall of Fame required;
- Cresselia/Lunar Wing sailor-child sequence completed;
- grant/enable Member Card through an existing Canalave interaction;
- remove `DISTRIBUTION_EVENT_DARKRAI`;
- level 50;
- retry-safe until captured.

## 6. Shaymin

Reuse Route 224/Seabreak Path/Flower Paradise.

Implement:
- Hall of Fame required;
- Route 224 accessible;
- Oak provides Oak's Letter in-game;
- remove `DISTRIBUTION_EVENT_SHAYMIN`;
- level 30;
- retry-safe until captured.

## 7. Arceus

Reuse Azure Flute/Hall of Origin.

Implement:
- Hall of Fame required;
- caught Dialga;
- caught Palkia;
- caught Giratina;
- Rowan/Cynthia grants Azure Flute;
- remove `DISTRIBUTION_EVENT_ARCEUS`;
- level 80;
- retry-safe until captured.

## 8. Manaphy / Phione

Sailor Eldritch gives a one-time Manaphy Egg after:
- Hall of Fame;
- Cresselia/Lunar Wing child sequence completed.

Rules:
- use native Manaphy Egg support;
- full party must not consume reward;
- received flag only after successful grant;
- D4 must preserve Manaphy + Ditto → Phione.

## 9. Rotom

Preserve Old Chateau and appliance-room mechanics.

Implement:
- remove `DISTRIBUTION_EVENT_ROTOM`;
- Secret Key becomes guaranteed from the Rotom encounter sequence or same-room pickup;
- form room remains permanently usable afterward;
- preserve all five appliance forms, move assignment, and recall behavior.

## 10. Regis / Regigigas

Reuse native Regi spaces:
- Regirock → Rock Peak Ruins;
- Regice → Iceberg Ruins;
- Registeel → Iron Ruins.

Remove event-Regigigas requirement.

Gate the trio on:
- Hall of Fame;
- normal map accessibility.

Each:
- one successful capture per save;
- retry-safe until captured.

Regigigas:
- Snowpoint Temple;
- require caught Regirock + Regice + Registeel;
- level 70;
- retry-safe until captured.

## 11. Legendary birds

Preserve Platinum's native roaming framework for:
- Articuno;
- Zapdos;
- Moltres.

Implement:
- all three obtainable in one save;
- remove unnecessary external/National-Dex acquisition dependency;
- deterministic reset if defeated uncaught;
- do not convert to ordinary grass encounters.

## 12. Legacy rare-habitat Legendary encounters

Add post-Hall-of-Fame renewable encounters exactly as follows:

| Species | Habitat | Method | Rate | Level |
|---|---|---|---:|---:|
| Mewtwo | deepest Turnback Cave rooms | cave | 1% | 68–72 |
| Raikou | Route 222 / Sunyshore electric coast | grass | 2% | 55–60 |
| Entei | Route 227 / Stark approach | grass | 2% | 55–60 |
| Suicune | Route 230 outer water | Surf | 2% | 55–60 |
| Lugia | Route 230 deep sea | Surf | 1% | 65–70 |
| Ho-Oh | Route 225 highland | grass | 1% | 65–70 |
| Latias | Route 229 | grass | 2% | 55–60 |
| Latios | Route 229 | grass | 2% | 55–60 |
| Groudon | Route 228 desert | grass | 1% | 65–70 |
| Kyogre | Route 223 deep water | Surf | 1% | 65–70 |
| Rayquaza | Route 224 terminus/highland | grass | 1% | 68–72 |

Rules:
- Hall of Fame flag required;
- no caught flag suppression;
- renewable indefinitely;
- normal legendary catch rates retained;
- no swarm/Radar/dual-slot dependency;
- preserve table density by replacing suitable postgame convenience slots rather than blindly adding slots;
- if the named conceptual habitat lacks the required encounter table, use the nearest map inside the same named habitat and document the mapping.

## 13. Older Mythical statics

Implement concise one-time, retry-safe discoveries:

- Mew — secluded Eterna Forest location — Lv50
- Celebi — Floaroma Meadow — Lv50
- Jirachi — upper Mt. Coronet/Spear Pillar approach — Lv50
- Deoxys — Veilstone meteorite area — Lv60

All require Hall of Fame.

Jirachi:
- night presentation preferred;
- time-of-day must not create permanent missability.

Deoxys:
- preserve meteorite form changes.

Prefer existing object slots/scripts. Do not create large custom quest chains.

## 14. Text policy

Reuse Platinum text where possible.

New dialogue should be short and functional:
- event-item reward;
- brief discovery flavor;
- retry/state text.

No long custom quest prose.

## 15. Runtime QA

At minimum test:
- Uxie/Azelf defeat then retry;
- Mesprit/Cresselia roamer defeat then reset;
- Giratina retry/fallback;
- both Dialga and Palkia;
- Heatran;
- Darkrai full unlock;
- Shaymin full unlock;
- Arceus prerequisite failure/success;
- Manaphy Egg with empty/full party;
- Phione breeding;
- Rotom forms;
- all three Regis + Regigigas;
- all three bird roamers;
- representative 2% and 1% legacy wilds;
- Mew, Celebi, Jirachi, Deoxys;
- Deoxys form change.

For every one-time static:
1. save before encounter;
2. defeat it;
3. leave/re-enter;
4. confirm retry;
5. capture;
6. confirm permanent completion.

## 16. Build order

Recommended commits:
1. manifests + validator;
2. native retry fixes;
3. Rotom;
4. Darkrai/Shaymin;
5. Arceus;
6. Manaphy/Phione;
7. Regis/Regigigas;
8. birds;
9. legacy rare habitats;
10. older Mythical statics;
11. final validation/status.

Build US Rev 0 and Rev 1 after script-sensitive batches and at final integration.

## 17. Status

Update:
- `docs/overhaul/STATUS.md`
- `docs/overhaul/DESIGN_PIPELINE.md`

Use:
- LOCKED SPEC
- IMPLEMENTING
- IMPLEMENTED
- VERIFIED

VERIFIED requires dual-revision builds, completion-graph validation, and representative runtime checks from every acquisition class.

## 18. Acceptance

D5 is complete when:
- every Legendary/Mythical #001–#493 is obtainable in one save;
- Sinnoh native event identity is preserved;
- older legends no longer require invented quest chains;
- all external dependencies are removed;
- one-time encounters are retry-safe;
- renewable legacy wilds match locked habitats/rates;
- both supported revisions build;
- runtime tests pass.
