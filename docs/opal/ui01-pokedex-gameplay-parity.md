# UI-01 — Gameplay-parity requirements for the Opal Pokédex

**Priority:** Gameplay truth takes precedence over cosmetics. The Pokédex must never present vanilla information as though it applies to Pokémon Opal.

## Design authority and verified facts

- `docs/overhaul/MASTER_SPEC.md`: all #001–#493 obtainable in one save, all nonlegendary families pre-Elite Four, no mandatory trading/second DS/WFC; wild availability favors lowest stages; legendary/mythical content is event/quest/gift/encounter oriented.
- `docs/overhaul/STATUS.md`: locked Pass B changes, C1 move changes, Pass A evolutions and C3H species/TM compatibility are implemented, with some battle/runtime QA pending.
- `docs/overhaul/MASTER_SPEC.md` lists implemented type directions such as Luxray Electric/Dark, Sceptile Grass/Dragon, Milotic Water/Dragon; species data and locked ledgers, not this summary, remain authoritative.

## Source-of-truth contract

| Player-facing surface | Truth source | Required implementation check |
| --- | --- | --- |
| Typing | Current compiled species personal data | Display actual type 1/2, never a copied original-type table |
| Abilities | Current species personal data and relevant ability unlock logic | Separate available ability slots from currently known individual's ability |
| Stats | Current compiled species personal data | Clearly label base stats versus an individual's observed stats |
| Evolution method | Current evolution tables and any custom evolution-method engine support | Derive method, threshold, location/time/item/condition and handle requirements that cannot be expressed in vanilla text |
| Habitat/location | Active wild encounter tables plus gifts/events and progression conditions | Avoid presenting unavailable/vanilla encounter zones; separate event-only and wild |
| Moves | Current level-up learnset data and TM/HM compatibility | Show Opal changes, and distinguish move learn timing vs TM eligibility |
| Form and language | Existing form, seen/caught and foreign-language unlock mechanics | Preserve all preexisting Dex functions and exact visibility rules |
| Completion tracking | Current captured/seen species state | Preserve #001–#493 and Sinnoh/National unlock logic; test final count |

## Content rules

1. Show only verified runtime facts. A roadmap item is not proof of an implemented change.
2. If a field cannot yet be populated from engine data, label it **not implemented** in the development plan; do not ship a speculative value.
3. Preserve seen/caught gating: do not reveal unavailable information earlier than the game's design allows without explicit approval.
4. Retain touch navigation, forms, cry, footprint, height/weight, map, sorting and international language behavior.
5. Keep the interface legible across both LCDs. Visual palette modernization supports this contract, not the other way around.
6. Prefer a versioned data-source adapter or generated manifest to manually authored Pokémon entries. Validate generated output against compiled tables after every gameplay overhaul update.

## First implementation milestone: Parity audit before new species panels

1. Enumerate current Pokédex display data sources, particularly how type, locations and descriptions are loaded.
2. Enumerate effective compiled species, evolution, learnset, move and wild encounter tables; match these to locked project ledgers.
3. Generate a machine-readable list of gameplay differences relative to vanilla Platinum and categorize what can be displayed with existing Pokédex UI versus needs additional views.
4. Define accurate UI treatments for species type/stat/ability, evolution, encounter source and moves. Keep descriptions and flavor text separate from mechanical facts.
5. Test representative retypes (Luxray, Sceptile, Milotic), non-trade evolutions, newly available pre-E4 families, and event Pokémon; only after this implement the new in-game panels.

**Release gate:** Build passing validates source compilation, not gameplay-data parity. Do not mark a Pokédex page complete until its display has been compared with the compiled gameplay data and emulator output.
