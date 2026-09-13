# Pokémon Platinum Overhaul — #001–#493 Availability Architecture

> **DRAFT PLAN — requires user approval**
>
> Planning only; this document does not authorize gameplay changes.

## 0. Canonical alignment and scope

This phase inherits the canonical overhaul boundaries: C1–C3, species identities, created moves, TM
compatibility, and **Pass A evolution design remain locked**. Availability provides a legitimate
family entry point; it does not redesign evolution methods or require trade, held-item trade, or any
other external evolution dependency. A pre-Elite Four family entry does not promise every evolved
member, form, or convenience item before the Elite Four unless the locked evolution spec requires it.

Architecture invariants:

* Generations I–IV may appear from the opening; Sinnoh receives no artificial early-game priority.
* Ecology, route identity, type choice, progression and low repetition determine placement.
* Prefer base stages; use middle stages sparingly and normally earn final stages.
* Every nonlegendary evolutionary family receives a deterministic pre-Elite Four entry at 5%+ or by
  a retry-safe guaranteed acquisition.
* No family or eventual #001–#493 completion depends on version, Slot-2, trading, WFC, a second
  system/save, external distribution, multiplayer, random fishing tiles, or an unbounded rotation.
* Special systems improve odds, levels, presentation or efficiency; they do not hold completion
  hostage.

## 1. Availability architecture (Pass 1)

| Band | Boundary | Availability role |
|---|---|---|
| E0 | start–Oreburgh | Cross-generation small fauna, bugs, birds, basic elemental/type choices; early Old Rod proposed |
| E1 | Oreburgh–Eterna | woodland, ghosts, fighters, rocks and first special-acquisition access |
| M1 | Eterna–Pastoria | central caves, pasture, ruins and wetlands; broad team-choice expansion |
| M2 | Pastoria–Canalave | Surf/Good Rod waters, industrial, steel, mineral and coastal families |
| L1 | Canalave–Snowpoint | cold, mountain, deep-cave and slower-evolving families |
| L2 | Snowpoint–eighth badge | dry, eastern-coast and high-power base families; Super Rod layer |
| P0 | eighth badge–Elite Four | final nonlegendary entry points and deterministic catch-up locations |
| P1 | Hall of Fame onward | evolved ecology, efficient recatches and later-phase legendary reservations |

**Density contract:** normally 6–8 families per 12-slot land/cave table (4–5 on connectors, at most
9 in a signature area) and 3–4 families per five-slot Surf/rod table. Adjacent habitats should share
no more than half their families unless they are visibly continuous. Rarity tiers are `C` 20–40%,
`U` 10–20%, `R` 5–10%, and `S` retry-safe guaranteed. Time-of-day may alter abundance, never sole
availability.

## 2. Encounter-zone framework

| Code | Identity |
|---|---|
| `START` | Twinleaf–Jubilife meadow, lake edge, farm fringe |
| `ORE` | Oreburgh mine, gate, quarry and rocky foothills |
| `FOREST` | Floaroma, Eterna woodland and Old Chateau |
| `CYCLE` | routes 206–208 scrub and Wayward Cave |
| `HEARTH` | Hearthome–Solaceon pasture, ruins and domestic species |
| `MARSH` | routes 212–213 and distinct stable Great Marsh habitats |
| `CORONET` | lower/upper mountain and progressively deeper strata |
| `IRON` | Fuego, Canalave and Iron Island industrial/coastal habitat |
| `COAST` | freshwater, estuary and sea pools separated by method |
| `SNOW` | routes 216–217, Acuity and cold interiors |
| `DRY` | route 214 and other reachable dry/savanna pockets |
| `EAST` | Valor–Sunyshore–route 223 electric/warm coast |
| `DEEP` | deep ruins, caves and Victory Road rare-family habitat |
| `POST` | routes 224–230, islands and Stark evolved convenience |

These are design regions, not approved exact map assignments.

## 3. Special-system policy

| System | Policy | Completion rule |
|---|---|---|
| Grass/caves, Surf, rods | keep/rebalance | primary deterministic distribution; rod tiers have distinct habitats |
| Honey Trees | keep/supplement | higher efficiency for tree families, never exclusive |
| Great Marsh | keep/supplement | stable area cores plus daily bonuses; Safari capture is not sole path |
| Poké Radar | keep/supplement | chaining/rarity bonus only |
| Swarms | keep/supplement | temporary abundance only |
| Trophy Garden | keep/supplement | rotating showcase; all residents have fixed alternatives |
| Dual-slot | replace as requirement | former species receive normal paths; cartridge state cannot affect completion |
| D/P exclusives | merge | both counterparts exist in one save |
| Daily/rotation | supplement only | no unique family behind real-time RNG |
| Gifts/statics | limited, retry-safe | each new or changed acquisition requires approval below |
| Underground/fossils | solo-capable | exact all-fossil method requires approval below |
| National Dex gating | remove from ordinary availability | exact UI/story timing requires approval below |
| Postgame | convenience + later-phase legends | never sole nonlegendary-family entry |

## 4. Problem-family exceptions (Pass 2)

| Conflict | Families/systems | Resolution boundary |
|---|---|---|
| Trade/external evolution | Kadabra, Machoke, Graveler, Haunter, Onix, Rhydon, Seadra, Scyther, Electabuzz, Magmar, Porygon, Slowpoke, Poliwhirl, Clamperl, etc. | Supply a family entry only; use the locked Evolution Spec, with no invented item gate. |
| Version/Slot-2 | counterpart pairs and Slot-2 species | Both receive ordinary pre-E4 entries; former cartridge slots may only be bonuses. |
| Radar/swarm-only | all Radar and swarm families | Fixed `R`/`U` habitat; special event raises frequency. |
| Honey-only | Combee, Burmy, Aipom, Heracross, Munchlax | Fixed 5%+ path; Honey is the efficient path. |
| Marsh/Garden rotation | rotating Marsh and Trophy Garden families | Stable area/route/gift alternative; rotation improves rate. |
| Fossils | Omanyte, Kabuto, Aerodactyl, Lileep, Anorith, Cranidos, Shieldon | Every family pre-E4 in one save; exact method awaits approval. |
| Awkward rarity | Feebas, Chansey, Kangaskhan, Lapras, Eevee, Porygon, Heracross, Munchlax, Chimecho | Fixed 5%+ or retry-safe guaranteed family entry. |
| Multiplayer | Spiritomb | Solo, retry-safe pre-E4 acquisition; exact quest awaits approval. |

## 5. USER APPROVAL REQUIRED

| Proposal | Recommendation | Simpler alternative | Consequence |
|---|---|---|---|
| Other starters | Staged, renewable habitat unlocks by Canalave | One NPC gives remaining starters in batches | Habitats preserve catching; gifts are much easier to script but less organic. |
| All fossils | Finite solo Underground discovery set, repeatable later | Museum NPC awards missing fossils at story gates | Underground stays relevant; NPC solution is simpler and more deterministic. |
| Spiritomb | Solo Odd Keystone exploration quest | Keystone directly activates Hallowed Tower | Quest preserves mystique but needs flags/dialogue; direct activation is minimal. |
| National Dex | Enable full UI/function early, tentatively by Eterna | Leave UI timing but remove National Dex checks from ordinary encounters | Early UI is clearer but touches story/UI scripts; encounter-only change is smaller. |
| Pseudo catch-up | Add a second `U` late-story habitat | Keep one fixed `R` habitat only | Catch-up reduces hunt friction but consumes scarce table capacity. |
| Rotom forms | Unlock appliances through its encounter follow-up | Make appliance room accessible with an existing story flag | Follow-up has better presentation; room access is simpler. |
| New/changed gifts/statics | Use only for unique flavor and always provide retry/fallback | Use ordinary 5%+ wild entries | Gifts improve presentation but require scripts, flags and missed-event handling. |
| Feebas | Fixed 10% Coronet basement pool | Fixed 5% Good Rod/Super Rod slot | Signature pool preserves identity; ordinary rod slot is simpler. |

## 6. Family availability matrix (Pass 3)

Confidence means: **LOCKED/OBVIOUS FIT** applies the approved invariant or an uncontroversial habitat;
**PROVISIONAL PLACEMENT** is a zone-level recommendation still needing manifest/source validation;
**SPECIAL DECISION REQUIRED** depends on section 5. No row locks an exact map, slot, level or percent.

### Kanto-rooted families

| Family / Dex range | Earliest | Area/system | Entry stage | Tier | Pre-E4 | Confidence | Note |
|---|---:|---|---|:---:|:---:|---|---|
| Bulbasaur 001–003 | E1 | FOREST starter method TBD | Bulbasaur | U | Y | SPECIAL DECISION REQUIRED | method requires approval |
| Charmander 004–006 | E1 | ORE starter method TBD | Charmander | U | Y | SPECIAL DECISION REQUIRED | method requires approval |
| Squirtle 007–009 | E1 | START lake starter method TBD | Squirtle | U | Y | SPECIAL DECISION REQUIRED | method requires approval |
| Caterpie 010–012 | E0 | START/FOREST | Caterpie | C | Y | LOCKED/OBVIOUS FIT | no version split |
| Weedle 013–015 | E0 | START/FOREST | Weedle | C | Y | LOCKED/OBVIOUS FIT | no version split |
| Pidgey 016–018 | E0 | START | Pidgey | C | Y | LOCKED/OBVIOUS FIT | — |
| Rattata 019–020 | E0 | START | Rattata | U | Y | LOCKED/OBVIOUS FIT | night-biased |
| Spearow 021–022 | E0 | ORE foothills | Spearow | U | Y | PROVISIONAL PLACEMENT | — |
| Ekans 023–024 | E1 | FOREST scrub | Ekans | U | Y | PROVISIONAL PLACEMENT | replaces dual-slot |
| Pikachu/Pichu 025–026,172 | E0 | START lake/forest | Pichu, Pikachu | R/U | Y | PROVISIONAL PLACEMENT | Trophy bonus |
| Sandshrew 027–028 | M1 | CYCLE quarry | Sandshrew | U | Y | PROVISIONAL PLACEMENT | replaces dual-slot |
| Nidoran♀ 029–031 | E0 | START meadow | Nidoran♀ | U | Y | PROVISIONAL PLACEMENT | Radar bonus |
| Nidoran♂ 032–034 | E0 | START meadow | Nidoran♂ | U | Y | PROVISIONAL PLACEMENT | Radar bonus |
| Clefairy/Cleffa 035–036,173 | E1 | CORONET lower | Clefairy | R | Y | PROVISIONAL PLACEMENT | baby by breeding; Garden bonus |
| Vulpix 037–038 | E1 | FOREST/Fuego edge | Vulpix | R | Y | PROVISIONAL PLACEMENT | replaces dual-slot |
| Jigglypuff/Igglybuff 039–040,174 | E1 | HEARTH meadow | Jigglypuff | U | Y | PROVISIONAL PLACEMENT | Garden bonus |
| Zubat 041–042,169 | E0 | ORE caves | Zubat | C | Y | LOCKED/OBVIOUS FIT | — |
| Oddish 043–045,182 | E1 | FOREST | Oddish | U | Y | PROVISIONAL PLACEMENT | — |
| Paras 046–047 | E1 | FOREST | Paras | U | Y | PROVISIONAL PLACEMENT | Marsh bonus |
| Venonat 048–049 | E1 | FOREST night | Venonat | U | Y | PROVISIONAL PLACEMENT | Radar bonus |
| Diglett 050–051 | E0 | ORE Mine | Diglett | U | Y | PROVISIONAL PLACEMENT | — |
| Meowth 052–053 | E0 | START/Jubilife fringe | Meowth | U | Y | PROVISIONAL PLACEMENT | Garden bonus |
| Psyduck 054–055 | E0 | START lake/ORE Gate | Psyduck | C | Y | LOCKED/OBVIOUS FIT | — |
| Mankey 056–057 | E0 | ORE foothills | Mankey | U | Y | PROVISIONAL PLACEMENT | Radar bonus |
| Growlithe 058–059 | E1 | FOREST/Fuego edge | Growlithe | R | Y | PROVISIONAL PLACEMENT | replaces dual-slot |
| Poliwag 060–062,186 | E1 | FOREST ponds; Old Rod | Poliwag | U | Y | PROVISIONAL PLACEMENT | — |
| Abra 063–065 | E0 | route 203/ORE Gate | Abra | U | Y | PROVISIONAL PLACEMENT | solo evolution per locked spec |
| Machop 066–068 | E0 | ORE Mine | Machop | U | Y | PROVISIONAL PLACEMENT | — |
| Bellsprout 069–071 | E1 | FOREST | Bellsprout | U | Y | PROVISIONAL PLACEMENT | — |
| Tentacool 072–073 | M1 | COAST Surf | Tentacool | C | Y | PROVISIONAL PLACEMENT | — |
| Geodude 074–076 | E0 | ORE | Geodude | C | Y | LOCKED/OBVIOUS FIT | — |
| Ponyta 077–078 | E1 | routes 205/206 grassland | Ponyta | U | Y | LOCKED/OBVIOUS FIT | — |
| Slowpoke 079–080,199 | M1 | MARSH/COAST freshwater | Slowpoke | U | Y | PROVISIONAL PLACEMENT | no version/Radar gate |
| Magnemite 081–082,462 | M1 | Fuego/IRON | Magnemite | C | Y | PROVISIONAL PLACEMENT | — |
| Farfetch'd 083 | E1 | FOREST clearing | Farfetch'd | R | Y | PROVISIONAL PLACEMENT | swarm bonus |
| Doduo 084–085 | M1 | CYCLE grassland | Doduo | U | Y | PROVISIONAL PLACEMENT | swarm bonus |
| Seel 086–087 | M2 | COAST cold water | Seel | U | Y | PROVISIONAL PLACEMENT | no version split |
| Grimer 088–089 | M1 | MARSH/Fuego | Grimer | U | Y | PROVISIONAL PLACEMENT | — |
| Shellder 090–091 | M2 | COAST Good Rod | Shellder | U | Y | PROVISIONAL PLACEMENT | — |
| Gastly 092–094 | E1 | Old Chateau | Gastly | C | Y | LOCKED/OBVIOUS FIT | — |
| Onix 095,208 | E0 | ORE Mine/Gate | Onix | U | Y | PROVISIONAL PLACEMENT | — |
| Drowzee 096–097 | M1 | HEARTH/route 215 | Drowzee | U | Y | PROVISIONAL PLACEMENT | swarm bonus |
| Krabby 098–099 | M1 | COAST Old/Good Rod | Krabby | U | Y | PROVISIONAL PLACEMENT | — |
| Voltorb 100–101 | M1 | Fuego | Voltorb | U | Y | PROVISIONAL PLACEMENT | swarm bonus |
| Exeggcute 102–103 | M1 | MARSH | Exeggcute | R | Y | PROVISIONAL PLACEMENT | stable subzone |
| Cubone 104–105 | E0 | ORE Mine deep | Cubone | R | Y | PROVISIONAL PLACEMENT | swarm bonus |
| Tyrogue/Hitmons 106–107,236–237 | M1 | CYCLE; entry method TBD | Tyrogue | S/R | Y | SPECIAL DECISION REQUIRED | gift versus habitat TBD |
| Lickitung 108,463 | M1 | HEARTH pasture | Lickitung | R | Y | PROVISIONAL PLACEMENT | swarm bonus |
| Koffing 109–110 | M1 | Fuego/IRON | Koffing | U | Y | PROVISIONAL PLACEMENT | — |
| Rhyhorn 111–112,464 | M1 | CORONET lower/quarry | Rhyhorn | U | Y | PROVISIONAL PLACEMENT | — |
| Happiny/Chansey 113,242,440 | M1 | HEARTH/route 210; entry TBD | Happiny or Chansey | S/R | Y | SPECIAL DECISION REQUIRED | Garden bonus |
| Tangela 114,465 | M1 | MARSH edge | Tangela | U | Y | PROVISIONAL PLACEMENT | — |
| Kangaskhan 115 | M1 | MARSH stable savanna | Kangaskhan | R | Y | PROVISIONAL PLACEMENT | daily bonus |
| Horsea 116–117,230 | M2 | COAST Good Rod | Horsea | U | Y | PROVISIONAL PLACEMENT | — |
| Goldeen 118–119 | E1 | freshwater Old Rod | Goldeen | U | Y | PROVISIONAL PLACEMENT | — |
| Staryu 120–121 | M2 | COAST Good Rod/night | Staryu | U | Y | PROVISIONAL PLACEMENT | — |
| Mime Jr./Mr. Mime 122,439 | M1 | HEARTH/route 209 | Mime Jr. | U | Y | PROVISIONAL PLACEMENT | Garden bonus |
| Scyther 123,212 | M1 | CYCLE/FOREST | Scyther | R | Y | PROVISIONAL PLACEMENT | no version split |
| Smoochum/Jynx 124,238 | L1 | SNOW | Smoochum, Jynx | U/R | Y | PROVISIONAL PLACEMENT | — |
| Elekid/Electabuzz 125,239,466 | M1 | Fuego | Elekid | U | Y | PROVISIONAL PLACEMENT | no dual-slot |
| Magby/Magmar 126,240,467 | M1 | Fuego | Magby | U | Y | PROVISIONAL PLACEMENT | no dual-slot |
| Pinsir 127 | M1 | FOREST deep | Pinsir | R | Y | PROVISIONAL PLACEMENT | no version split |
| Tauros 128 | M1 | HEARTH pasture | Tauros | R | Y | PROVISIONAL PLACEMENT | Radar bonus |
| Magikarp 129–130 | E0 | Old Rod | Magikarp | C | Y | LOCKED/OBVIOUS FIT | not the whole rod pool |
| Lapras 131 | M2 | IRON/COAST cavern Surf | Lapras | R | Y | PROVISIONAL PLACEMENT | fixed 5%+ pool |
| Ditto 132 | M1 | Trophy Garden core/route 218 | Ditto | R | Y | PROVISIONAL PLACEMENT | deterministic |
| Eevee 133–136,196–197,470–471 | M1 | Hearthome/Garden; entry TBD | Eevee | S/R | Y | SPECIAL DECISION REQUIRED | gift versus wild TBD |
| Porygon 137,233,474 | M2 | Veilstone/Garden; entry TBD | Porygon | S/R | Y | SPECIAL DECISION REQUIRED | locked evolution only |
| Omanyte 138–139 | E1 | fossil method TBD | Omanyte | S | Y | SPECIAL DECISION REQUIRED | — |
| Kabuto 140–141 | E1 | fossil method TBD | Kabuto | S | Y | SPECIAL DECISION REQUIRED | — |
| Aerodactyl 142 | E1 | fossil method TBD | Aerodactyl | S | Y | SPECIAL DECISION REQUIRED | — |
| Snorlax/Munchlax 143,446 | E1 | Honey/FOREST grove | Munchlax | R | Y | PROVISIONAL PLACEMENT | Honey common; no tree lottery |
| Dratini 147–149 | M2 | CORONET hidden lake/Good Rod | Dratini | R | Y | PROVISIONAL PLACEMENT | late catch-up placement TBD |
### Johto-rooted families

| Family / Dex range | Earliest | Area/system | Entry stage | Tier | Pre-E4 | Confidence | Note |
|---|---:|---|---|:---:|:---:|---|---|
| Chikorita 152–154 | M1 | HEARTH starter method TBD | Chikorita | U | Y | SPECIAL DECISION REQUIRED | method requires approval |
| Cyndaquil 155–157 | M1 | Fuego starter method TBD | Cyndaquil | U | Y | SPECIAL DECISION REQUIRED | method requires approval |
| Totodile 158–160 | M1 | MARSH starter method TBD | Totodile | U | Y | SPECIAL DECISION REQUIRED | method requires approval |
| Sentret 161–162 | E0 | START | Sentret | U | Y | PROVISIONAL PLACEMENT | Radar bonus |
| Hoothoot 163–164 | E0 | START/FOREST night | Hoothoot | C | Y | LOCKED/OBVIOUS FIT | — |
| Ledyba 165–166 | E0 | START morning | Ledyba | U | Y | PROVISIONAL PLACEMENT | all-day forest fallback |
| Spinarak 167–168 | E0 | START night | Spinarak | U | Y | LOCKED/OBVIOUS FIT | all-day forest fallback |
| Chinchou 170–171 | M2 | COAST Good Rod | Chinchou | U | Y | LOCKED/OBVIOUS FIT | — |
| Togepi 175–176,468 | E1 | Eterna egg + HEARTH | Togepi | S/R | Y | PROVISIONAL PLACEMENT | repeatable source |
| Natu 177–178 | M1 | Solaceon Ruins exterior | Natu | U | Y | PROVISIONAL PLACEMENT | swarm bonus |
| Mareep 179–181 | E0 | START meadow | Mareep | U | Y | LOCKED/OBVIOUS FIT | early Electric choice |
| Marill/Azurill 183–184,298 | E1 | Floaroma/FOREST ponds | Marill | U | Y | PROVISIONAL PLACEMENT | baby by early incense; Garden bonus |
| Hoppip 187–189 | E0 | Floaroma/START | Hoppip | U | Y | PROVISIONAL PLACEMENT | Radar bonus |
| Aipom 190,424 | E1 | FOREST canopy/Honey | Aipom | R | Y | PROVISIONAL PLACEMENT | Honey common |
| Sunkern 191–192 | E1 | Floaroma fields | Sunkern | U | Y | PROVISIONAL PLACEMENT | Radar bonus |
| Yanma 193,469 | M1 | MARSH stable pond | Yanma | U | Y | LOCKED/OBVIOUS FIT | — |
| Wooper 194–195 | E1 | FOREST ponds | Wooper | U | Y | LOCKED/OBVIOUS FIT | — |
| Murkrow 198,430 | E1 | FOREST/Old Chateau night | Murkrow | U | Y | LOCKED/OBVIOUS FIT | no version split |
| Misdreavus 200,429 | E1 | Old Chateau night | Misdreavus | U | Y | LOCKED/OBVIOUS FIT | no version split |
| Unown 201 | M1 | Solaceon Ruins | Unown | C | Y | LOCKED/OBVIOUS FIT | forms are collection extras |
| Wobbuffet/Wynaut 202,360 | M1 | CORONET lower | Wynaut/Wobbuffet | R | Y | PROVISIONAL PLACEMENT | Radar bonus |
| Girafarig 203 | M1 | HEARTH/route 210 | Girafarig | U | Y | PROVISIONAL PLACEMENT | — |
| Pineco 204–205 | E1 | FOREST/Honey | Pineco | R | Y | PROVISIONAL PLACEMENT | — |
| Dunsparce 206 | E0 | ORE Gate side room | Dunsparce | R | Y | PROVISIONAL PLACEMENT | swarm bonus |
| Gligar 207,472 | M1 | CYCLE/Wayward Cave | Gligar | U | Y | PROVISIONAL PLACEMENT | no dual-slot |
| Snubbull 209–210 | M1 | HEARTH pasture | Snubbull | U | Y | PROVISIONAL PLACEMENT | swarm bonus |
| Qwilfish 211 | M2 | COAST Good Rod | Qwilfish | U | Y | PROVISIONAL PLACEMENT | — |
| Shuckle 213 | M1 | CYCLE quarry rocks | Shuckle | R | Y | PROVISIONAL PLACEMENT | no dual-slot |
| Heracross 214 | E1 | FOREST/Honey | Heracross | R | Y | PROVISIONAL PLACEMENT | Honey common |
| Sneasel 215,461 | L1 | SNOW | Sneasel | C | Y | LOCKED/OBVIOUS FIT | — |
| Teddiursa 216–217 | E1 | FOREST deep | Teddiursa | U | Y | PROVISIONAL PLACEMENT | no dual-slot |
| Slugma 218–219 | M1 | Fuego | Slugma | U | Y | PROVISIONAL PLACEMENT | — |
| Swinub 220–221,473 | L1 | SNOW | Swinub | C | Y | LOCKED/OBVIOUS FIT | swarm bonus |
| Corsola 222 | M2 | COAST Good Rod | Corsola | R | Y | PROVISIONAL PLACEMENT | swarm bonus |
| Remoraid 223–224 | M1 | freshwater Good Rod | Remoraid | U | Y | PROVISIONAL PLACEMENT | — |
| Delibird 225 | L1 | SNOW | Delibird | U | Y | PROVISIONAL PLACEMENT | swarm bonus |
| Mantyke/Mantine 226,458 | M2 | COAST Surf | Mantyke | U | Y | PROVISIONAL PLACEMENT | Remoraid available |
| Skarmory 227 | M2 | IRON exterior | Skarmory | R | Y | PROVISIONAL PLACEMENT | — |
| Houndour 228–229 | M1 | route 214/night | Houndour | U | Y | LOCKED/OBVIOUS FIT | Radar bonus |
| Phanpy 231–232 | M1 | CYCLE quarry | Phanpy | U | Y | PROVISIONAL PLACEMENT | swarm bonus |
| Stantler 234 | M1 | route 210/FOREST edge | Stantler | R | Y | PROVISIONAL PLACEMENT | swarm bonus |
| Smeargle 235 | M1 | HEARTH artist meadow | Smeargle | R | Y | PROVISIONAL PLACEMENT | Radar bonus |
| Miltank 241 | M1 | HEARTH pasture | Miltank | R | Y | PROVISIONAL PLACEMENT | — |
| Larvitar 246–248 | L1 | CORONET upper | Larvitar | R | Y | PROVISIONAL PLACEMENT | late catch-up placement TBD |
### Hoenn-rooted families

| Family / Dex range | Earliest | Area/system | Entry stage | Tier | Pre-E4 | Confidence | Note |
|---|---:|---|---|:---:|:---:|---|---|
| Treecko 252–254 | M1 | FOREST starter method TBD | Treecko | U | Y | SPECIAL DECISION REQUIRED | method requires approval |
| Torchic 255–257 | M1 | Fuego starter method TBD | Torchic | U | Y | SPECIAL DECISION REQUIRED | method requires approval |
| Mudkip 258–260 | M1 | MARSH starter method TBD | Mudkip | U | Y | SPECIAL DECISION REQUIRED | method requires approval |
| Poochyena 261–262 | E0 | START night | Poochyena | U | Y | LOCKED/OBVIOUS FIT | — |
| Zigzagoon 263–264 | E0 | START | Zigzagoon | U | Y | LOCKED/OBVIOUS FIT | swarm bonus |
| Wurmple 265–269 | E0 | START/FOREST | Wurmple | C | Y | LOCKED/OBVIOUS FIT | — |
| Lotad 270–272 | E1 | FOREST ponds | Lotad | U | Y | PROVISIONAL PLACEMENT | no dual-slot/version gate |
| Seedot 273–275 | E1 | FOREST | Seedot | U | Y | PROVISIONAL PLACEMENT | no dual-slot/version gate |
| Taillow 276–277 | E0 | START/open routes | Taillow | U | Y | LOCKED/OBVIOUS FIT | — |
| Wingull 278–279 | E1 | Floaroma/Canalave waterways | Wingull | U | Y | LOCKED/OBVIOUS FIT | — |
| Ralts 280–282,475 | E1 | FOREST/HEARTH | Ralts | R | Y | PROVISIONAL PLACEMENT | Radar bonus |
| Surskit 283–284 | E1 | FOREST ponds | Surskit | U | Y | PROVISIONAL PLACEMENT | swarm bonus |
| Shroomish 285–286 | E1 | FOREST deep | Shroomish | R | Y | PROVISIONAL PLACEMENT | Marsh bonus |
| Slakoth 287–289 | E1 | FOREST canopy | Slakoth | R | Y | PROVISIONAL PLACEMENT | swarm bonus |
| Nincada 290–292 | E1 | FOREST/ORE soil | Nincada | U | Y | PROVISIONAL PLACEMENT | party-slot evolution support |
| Whismur 293–295 | E0 | ORE Gate | Whismur | U | Y | LOCKED/OBVIOUS FIT | Radar bonus |
| Makuhita 296–297 | E0 | ORE Mine/training area | Makuhita | U | Y | PROVISIONAL PLACEMENT | swarm bonus |
| Nosepass 299,476 | E0 | ORE Mine | Nosepass | R | Y | PROVISIONAL PLACEMENT | swarm bonus |
| Skitty 300–301 | E1 | Floaroma/HEARTH | Skitty | U | Y | PROVISIONAL PLACEMENT | swarm bonus |
| Sableye 302 | E1 | Old Chateau/Wayward Cave | Sableye | R | Y | PROVISIONAL PLACEMENT | no dual-slot/version gate |
| Mawile 303 | M1 | IRON/Wayward Cave | Mawile | R | Y | PROVISIONAL PLACEMENT | no dual-slot/version gate |
| Aron 304–306 | M1 | IRON | Aron | U | Y | LOCKED/OBVIOUS FIT | Radar bonus |
| Meditite 307–308 | E0 | ORE foothills | Meditite | U | Y | LOCKED/OBVIOUS FIT | — |
| Electrike 309–310 | M1 | Fuego/route 214 | Electrike | U | Y | PROVISIONAL PLACEMENT | swarm bonus |
| Plusle 311 | M1 | Trophy Garden/Fuego | Plusle | R | Y | PROVISIONAL PLACEMENT | deterministic pair |
| Minun 312 | M1 | Trophy Garden/Fuego | Minun | R | Y | PROVISIONAL PLACEMENT | deterministic pair |
| Volbeat 313 | M1 | MARSH night | Volbeat | U | Y | PROVISIONAL PLACEMENT | — |
| Illumise 314 | M1 | MARSH night | Illumise | U | Y | PROVISIONAL PLACEMENT | — |
| Roselia/Budew 315,406–407 | E0 | START/Floaroma | Budew | C | Y | PROVISIONAL PLACEMENT | — |
| Gulpin 316–317 | M1 | MARSH stable mire | Gulpin | U | Y | PROVISIONAL PLACEMENT | daily bonus |
| Carvanha 318–319 | M1 | MARSH/COAST Good Rod | Carvanha | U | Y | PROVISIONAL PLACEMENT | — |
| Wailmer 320–321 | M2 | COAST Good Rod | Wailmer | U | Y | PROVISIONAL PLACEMENT | — |
| Numel 322–323 | M1 | Fuego/DRY | Numel | U | Y | PROVISIONAL PLACEMENT | — |
| Torkoal 324 | M1 | Fuego | Torkoal | R | Y | PROVISIONAL PLACEMENT | Radar bonus |
| Spoink 325–326 | M1 | route 214/HEARTH | Spoink | U | Y | PROVISIONAL PLACEMENT | swarm bonus |
| Spinda 327 | M1 | DRY | Spinda | U | Y | PROVISIONAL PLACEMENT | swarm bonus |
| Trapinch 328–330 | M1 | DRY/Wayward deep | Trapinch | R | Y | PROVISIONAL PLACEMENT | Radar bonus |
| Cacnea 331–332 | M1 | DRY | Cacnea | U | Y | PROVISIONAL PLACEMENT | — |
| Swablu 333–334 | M1 | CORONET foothills | Swablu | U | Y | PROVISIONAL PLACEMENT | Radar bonus |
| Zangoose 335 | M1 | route 210/215 border | Zangoose | R | Y | PROVISIONAL PLACEMENT | paired, no version gate |
| Seviper 336 | M1 | route 210/215 border | Seviper | R | Y | PROVISIONAL PLACEMENT | paired, no version gate |
| Lunatone 337 | M1 | CORONET night | Lunatone | R | Y | PROVISIONAL PLACEMENT | no dual-slot |
| Solrock 338 | M1 | CORONET day | Solrock | R | Y | PROVISIONAL PLACEMENT | all-day deep-room fallback |
| Barboach 339–340 | E1 | freshwater Old/Good Rod | Barboach | U | Y | LOCKED/OBVIOUS FIT | — |
| Corphish 341–342 | M1 | MARSH Good Rod | Corphish | U | Y | PROVISIONAL PLACEMENT | — |
| Baltoy 343–344 | M1 | Solaceon Ruins/DRY | Baltoy | U | Y | PROVISIONAL PLACEMENT | Radar bonus |
| Lileep 345–346 | E1 | fossil method TBD | Lileep | S | Y | SPECIAL DECISION REQUIRED | — |
| Anorith 347–348 | E1 | fossil method TBD | Anorith | S | Y | SPECIAL DECISION REQUIRED | — |
| Feebas 349–350 | M1 | CORONET fixed basement pool | Feebas | U | Y | PROVISIONAL PLACEMENT | no random tiles |
| Castform 351 | M1 | Trophy Garden/weather gift | Castform | S/R | Y | SPECIAL DECISION REQUIRED | deterministic |
| Kecleon 352 | M1 | FOREST/route 210 | Kecleon | R | Y | PROVISIONAL PLACEMENT | no dual-slot/Radar gate |
| Shuppet 353–354 | E1 | Old Chateau | Shuppet | U | Y | LOCKED/OBVIOUS FIT | — |
| Duskull 355–356,477 | E1 | Old Chateau/DEEP | Duskull | U | Y | LOCKED/OBVIOUS FIT | — |
| Tropius 357 | M1 | MARSH savanna | Tropius | R | Y | PROVISIONAL PLACEMENT | stable subzone |
| Chingling/Chimecho 358,433 | M1 | CORONET/route 211 | Chingling | R | Y | PROVISIONAL PLACEMENT | fixed 5%+ |
| Absol 359 | L1 | CORONET/SNOW approach | Absol | R | Y | PROVISIONAL PLACEMENT | swarm bonus |
| Snorunt 361–362,478 | L1 | SNOW | Snorunt | U | Y | LOCKED/OBVIOUS FIT | Radar bonus; Dawn Stone pre-E4 |
| Spheal 363–365 | L1 | SNOW/COAST | Spheal | U | Y | LOCKED/OBVIOUS FIT | — |
| Clamperl 366–368 | M2 | COAST Super Rod | Clamperl | U | Y | PROVISIONAL PLACEMENT | locked evolution only |
| Relicanth 369 | L2 | COAST Super Rod | Relicanth | R | Y | PROVISIONAL PLACEMENT | — |
| Luvdisc 370 | M2 | COAST Good Rod | Luvdisc | U | Y | PROVISIONAL PLACEMENT | — |
| Bagon 371–373 | L1 | DEEP cave | Bagon | R | Y | PROVISIONAL PLACEMENT | late catch-up placement TBD |
| Beldum 374–376 | M2 | IRON deep/static | Beldum | R/S | Y | PROVISIONAL PLACEMENT | swarm bonus |
### Sinnoh-rooted families

| Family / Dex range | Earliest | Area/system | Entry stage | Tier | Pre-E4 | Confidence | Note |
|---|---:|---|---|:---:|:---:|---|---|
| Turtwig 387–389 | E0 | starter/starter method TBD | Turtwig | S/U | Y | SPECIAL DECISION REQUIRED | unchosen available by Eterna |
| Chimchar 390–392 | E0 | starter/starter method TBD | Chimchar | S/U | Y | SPECIAL DECISION REQUIRED | unchosen available by Eterna |
| Piplup 393–395 | E0 | starter/starter method TBD | Piplup | S/U | Y | SPECIAL DECISION REQUIRED | unchosen available by Eterna |
| Starly 396–398 | E0 | START | Starly | C | Y | LOCKED/OBVIOUS FIT | integrated, not privileged |
| Bidoof 399–400 | E0 | START | Bidoof | C | Y | LOCKED/OBVIOUS FIT | integrated, not dominant |
| Kricketot 401–402 | E0 | START | Kricketot | U | Y | LOCKED/OBVIOUS FIT | all-day fallback |
| Shinx 403–405 | E0 | START | Shinx | U | Y | LOCKED/OBVIOUS FIT | shares Electric role with Mareep/Pikachu |
| Cranidos 408–409 | E1 | fossil method TBD | Cranidos | S | Y | SPECIAL DECISION REQUIRED | no version restriction |
| Shieldon 410–411 | E1 | fossil method TBD | Shieldon | S | Y | SPECIAL DECISION REQUIRED | no version restriction |
| Burmy 412–414 | E1 | FOREST/Honey | Burmy | R | Y | PROVISIONAL PLACEMENT | Honey common; cloak habitats retained |
| Combee 415–416 | E1 | Floaroma/FOREST/Honey | Combee | U | Y | PROVISIONAL PLACEMENT | no Honey bottleneck |
| Pachirisu 417 | E0 | Floaroma/START | Pachirisu | U | Y | LOCKED/OBVIOUS FIT | — |
| Buizel 418–419 | E1 | Floaroma waterways | Buizel | C | Y | LOCKED/OBVIOUS FIT | — |
| Cherubi 420–421 | E1 | Floaroma/FOREST | Cherubi | U | Y | PROVISIONAL PLACEMENT | Honey bonus |
| Shellos 422–423 | E1 | west water; east form M2 | Shellos | U | Y | LOCKED/OBVIOUS FIT | both forms in one save |
| Drifloon 425–426 | E1 | Valley Windworks | Drifloon | R/S | Y | PROVISIONAL PLACEMENT | not Friday-only; static respawns |
| Buneary 427–428 | E1 | FOREST | Buneary | U | Y | LOCKED/OBVIOUS FIT | — |
| Glameow 431–432 | E1 | Floaroma/HEARTH | Glameow | U | Y | PROVISIONAL PLACEMENT | D/P exclusive merged |
| Stunky 434–435 | E1 | FOREST/route 206 | Stunky | U | Y | PROVISIONAL PLACEMENT | D/P exclusive merged |
| Bronzor 436–437 | M1 | CORONET/Solaceon Ruins | Bronzor | C | Y | LOCKED/OBVIOUS FIT | — |
| Bonsly/Sudowoodo 438,185 | M1 | Trophy Garden/route 209 | Bonsly | U | Y | PROVISIONAL PLACEMENT | deterministic |
| Chatot 441 | M1 | COAST/route 213 | Chatot | U | Y | PROVISIONAL PLACEMENT | in-game trade optional |
| Spiritomb 442 | M1 | Spiritomb method TBD | Spiritomb static | S | Y | SPECIAL DECISION REQUIRED | no multiplayer |
| Gible 443–445 | M1 | Wayward Cave deep | Gible | R | Y | PROVISIONAL PLACEMENT | late catch-up placement TBD |
| Riolu 447–448 | M2 | Iron Island; entry TBD | Riolu | S/R | Y | SPECIAL DECISION REQUIRED | gift fallback TBD |
| Hippopotas 449–450 | M1 | Ruin Maniac/DRY | Hippopotas | U | Y | LOCKED/OBVIOUS FIT | — |
| Skorupi 451–452 | M1 | MARSH stable mire | Skorupi | U | Y | LOCKED/OBVIOUS FIT | — |
| Croagunk 453–454 | M1 | MARSH | Croagunk | C | Y | LOCKED/OBVIOUS FIT | — |
| Carnivine 455 | M1 | MARSH stable deep bog | Carnivine | R | Y | PROVISIONAL PLACEMENT | daily bonus |
| Finneon 456–457 | M1 | COAST Good Rod | Finneon | U | Y | LOCKED/OBVIOUS FIT | — |
| Snover 459–460 | L1 | SNOW | Snover | C | Y | LOCKED/OBVIOUS FIT | — |
| Rotom 479 | E1 | Old Chateau; entry TBD | Rotom | S | Y | SPECIAL DECISION REQUIRED | form method also TBD |
## 7. Legendary/Mythical reservation

All Legendary and Mythical species within #001–#493 are reserved to the later Legendary/Mythical
phase. That phase owns encounter/quest/form design and must provide every species in one save without
external distribution, version, hardware, network or multiplayer requirements. This document makes
no quest decisions for them.

## 8. Completion audit and Claude handoff

### Required manifests

| Manifest | Minimum fields |
|---|---|
| family availability | locked evolution component, classification, earliest gate, renewable entry, dependency flags |
| encounter zones | map, zone, story gate, methods, level band, family budget |
| wild slots | map/method/slot, species/stage, level, rate tier, time condition, bonus system |
| special acquisition | approved gifts/statics, fossils, Spiritomb, Rotom, retry/fallback semantics |
| special pools | Honey, Marsh, Radar, swarms, Garden, former dual-slot slots, fixed fallback link |
| legendary reservation | species and later-phase ownership only |

### Implementation order after approval

1. Reconcile approved choices into the family graph and create data manifests.
2. Remove ordinary-species National Dex/external gates.
3. Generate E0–P0 land/cave tables, then Surf/rod tables, validating each band.
4. Implement only approved special acquisitions and bonus-system changes.
5. Add postgame convenience tables; leave Legendary/Mythical work to its owning phase.

### Validators and acceptance

* Build families from locked evolution data; every nonlegendary component has a `PRE_E4` entry.
* Every #001–#493 species is either reachable through that component or reserved to the later phase.
* Fail sole paths tagged version, Slot-2, trade, WFC, external, multiplayer, random-tile or rotation.
* Fail required wild rates below 5%, over-budget tables, inaccessible methods, or missing retry paths.
* Manually check branching/gender/baby cases, Shedinja, Shellos forms and Rotom form non-requirement.
* Exact map/slot/level/percentage manifests require separate review before gameplay implementation.
