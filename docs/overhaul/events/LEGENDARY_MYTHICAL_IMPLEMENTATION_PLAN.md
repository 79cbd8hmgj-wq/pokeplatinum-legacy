# Pokémon Platinum Overhaul — Legendary/Mythical Implementation Plan

Status: **LOCKED IMPLEMENTATION PLAN**

Authority:
- `docs/overhaul/events/LEGENDARY_MYTHICAL_SPEC.md`

Claude Code implements; it must not redesign event placements or prerequisites.

## 1. Native-event audit

Before edits, map:
- event script;
- init script;
- event object;
- flag/var;
- item gate;
- distribution gate;
- encounter level;
- retry behavior

for:
- Darkrai/Newmoon;
- Shaymin/Route 224/Flower Paradise;
- Arceus/Spear Pillar/Hall of Origin;
- Rotom/Secret Key room;
- Regi ruins;
- Regigigas;
- Dialga/Palkia;
- Giratina;
- Heatran;
- Mesprit;
- Cresselia;
- roaming birds.

Create:
`docs/overhaul/implementation/events/native_legendary_audit.json`

## 2. Event manifest

Create:
`docs/overhaul/implementation/events/legendary_events.json`

Fields:
- species;
- event_id;
- class: native_ungate/native_adjust/new_static/new_gift/roamer;
- map;
- level;
- prerequisites;
- required items;
- flags/vars;
- external gate removed;
- retry behavior;
- post-capture state;
- dependencies.

Validator must prove all Legendary/Mythical species through #493 are represented.

## 3. L1 — native distribution ungates

Implement first:
- Darkrai;
- Shaymin;
- Arceus;
- Rotom forms;
- Regirock/Regice/Registeel;
- Regigigas.

Prefer deleting/replacing only local distribution/fateful checks.

Do not globally alter Mystery Gift/distribution-event infrastructure.

## 4. L2 — retry-safe native encounters

Audit and repair retry behavior for:
- Uxie/Azelf;
- Mesprit;
- Cresselia;
- Giratina;
- Heatran;
- Dialga;
- Palkia;
- birds;
- Darkrai;
- Shaymin;
- Arceus;
- Regis/Regigigas.

Captured state must be distinct from defeated state.

Implement a deterministic Hall-of-Fame or postgame reset path for defeated roamers.

## 5. L3 — event-item acquisition

Implement internal acquisition for:
- Member Card;
- Oak's Letter;
- Azure Flute;
- Secret Key.

Then add any required internal keys:
- Silver Wing;
- Rainbow Wing;
- Red Orb;
- Blue Orb;
- research/meteorite state.

Use existing IDs if present.

If a proposed new key ID conflicts with live data, stop only that item and report the smallest alternative.

## 6. L4 — new static quest encounters

Implement in small families:
- Mewtwo → Mew;
- Raikou/Entei/Suicune → Ho-Oh/Lugia;
- Kyogre/Groudon → Rayquaza;
- Jirachi → Deoxys.

Prefer existing maps and event-object slots.

Do not create new maps unless the spec's preferred location cannot be represented coherently.

If a preferred broad location has several valid existing maps, Claude may choose the technically cleanest map within that named location; this is implementation mapping, not redesign.

## 7. L5 — Manaphy Egg

Implement retry-safe gift:
- postgame Canalave sailor chain;
- requires Cresselia/sailor-child resolution and Iron Island completion;
- give Manaphy Egg only when party has room;
- if full/refused, remain claimable;
- set received flag only after successful grant.

Validate Phione breeding with D4 rules.

## 8. L6 — Arceus capstone

Only after Dialga/Palkia/Giratina caught:
- grant Azure Flute;
- activate Hall of Origin;
- remove distribution gate;
- preserve Lv80 encounter and native presentation.

Ensure no conflict among Spear Pillar rift states.

## 9. Roamer constraint

Current source has six fixed roaming slots:
- Mesprit;
- Cresselia;
- Darkrai;
- Moltres;
- Zapdos;
- Articuno.

Do not expand this table for Johto beasts/Latias/Latios in Core 1.0.

Use the locked static solutions.

Darkrai should remain static on Newmoon for the restored Member Card event; do not activate its unused/alternate roamer slot unless source proves it is part of the intended sequence.

## 10. Validator

Create:
`tools/overhaul/validate_legendary_events.py`

Fail on:
- species missing internal source;
- distribution/WFC/migration/trade/multiplayer dependency;
- circular prerequisite;
- gift that can be lost due to full party;
- static permanently removed on defeat;
- captured flag set without capture;
- duplicate conflicting event ownership;
- Hall of Origin reachable before locked prerequisites;
- Regi ruin still requires fateful external Regigigas;
- Rotom room still requires distribution event.

Generate:
`docs/overhaul/implementation/events/LEGENDARY_EVENT_VALIDATION_REPORT.md`

## 11. Runtime batches

Test at least:
- Darkrai full Member Card chain;
- Shaymin Oak's Letter chain;
- Rotom Secret Key/forms;
- all three Regi puzzles;
- Regigigas;
- Dialga/Palkia retry;
- Giratina retry path;
- one defeated roamer reactivation;
- Manaphy Egg full-party retry;
- each new imported-legend chain;
- Arceus capstone.

For every static:
1. save before battle;
2. defeat it;
3. leave/re-enter;
4. confirm respawn;
5. capture;
6. confirm permanent completion.

## 12. Builds

Build US Rev 0 and Rev 1 after:
- native ungates;
- Regi/Rotom changes;
- imported static events;
- Arceus final integration.

## 13. Commit structure

Recommended:
1. manifests + validator;
2. Darkrai/Shaymin/Rotom;
3. Regis/Regigigas;
4. Dialga/Palkia/Giratina/native retry fixes;
5. Manaphy;
6. Kanto/Johto imported legends;
7. Hoenn imported legends;
8. Arceus;
9. final validation/status.

## 14. Status

Update:
- `docs/overhaul/STATUS.md`;
- `docs/overhaul/DESIGN_PIPELINE.md`.

VERIFIED requires dual-revision builds plus runtime validation of every event class and completion-graph validator pass.
