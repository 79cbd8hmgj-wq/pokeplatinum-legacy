# Pass G — Delta Render Review Checklist

Status: **manual QA pending**

This checklist is the final subjective gate after source-side completion of G5/G6.
Do not make new visual edits unless a specific issue is observed in Delta.

## Test conditions

Use the current visual-overhaul branch ROM in Delta with:
- no external texture packs
- no emulator-side post-processing or shader assumptions
- normal DS display scaling
- both day and night/evening where noted

Capture a screenshot for any defect before changing source.

## Environment showcase review

### Eterna Forest
Check:
- player/NPC sprites remain readable against the darker green palette
- canopy mist does not wash out paths or collision edges
- the dedicated camera framing does not clip props or hide navigation cues
- forest ambience sparkle frequency feels subtle rather than constant
- day lighting retains enough depth between ground, underbrush, trees, and shadows
- night/dawn does not become too flat or too dark

Reject only if:
- navigation becomes unclear
- ambience distracts from movement
- major props merge into the background
- camera framing causes actual readability/collision perception problems

### Snowpoint City
Check:
- snow remains the brightest dominant surface
- exposed vegetation no longer looks fluorescent
- buildings and paths remain distinct from the snow
- daylight/evening color shifts remain readable

### Route 217
Check:
- blizzard particles plus fog do not obscure the player
- terrain edges remain visible during movement
- snowbanks/trees retain separation under heavy weather
- the cooler environment grade does not turn the scene uniformly blue

### Distortion World
Check:
- dark stone retains internal contrast
- violet/magenta accents remain distinct without clipping into neon
- blue accents remain visible but controlled
- Giratina/character silhouettes remain readable
- special fog adds depth rather than flattening the scene

### Spear Pillar
Check:
- summit stone reads as cool ancient stone rather than gray mush
- fog retains distant depth
- player/NPC/legendary silhouettes remain clear
- sky/fog/stone values do not collapse together

### Sinnoh lakes
Check:
- water is clearly separated from shoreline highlights
- vegetation remains natural rather than fluorescent
- reflections/highlights are visible without dominating
- zoomed-in camera still presents the scene cleanly

### Turnback Cave
Check:
- fog does not erase wall/floor separation
- cave remains intentionally dark without hiding navigation
- special bright material/key colors do not appear as accidental neon artifacts
- room transitions retain their intended look

### Team Galactic interiors
Check:
- cool industrial grade retains floor/wall/object separation
- monitors, desks, doors, and interaction targets remain readable
- warehouse grade matches the main Galactic visual language without losing its own material identity
- no shared generic interior outside Galactic areas appears accidentally recolored

## Battle presentation spot-check

The purpose is to validate proportionality, not to inspect every edited move.

### Heavy collision tier
Test:
- Giga Impact
- Head Smash
- Hydro Cannon
- Blast Burn
- Volt Tackle

Expected:
- base arena reacts clearly at the decisive hit
- shake is stronger than ordinary attacks
- effect-background motion and arena motion do not visually fight each other
- no lingering offset or camera/background desync remains after the move

### Medium/restrained impact tier
Test:
- Fire Blast
- Shadow Ball
- Meteor Mash
- Cross Chop
- Seed Flare

Expected:
- extra staging is perceptible but not excessive
- the arena reaction does not make these feel identical to the heaviest attacks

### Scene-grade identity
Test:
- Aura Sphere
- Energy Ball
- Flash Cannon
- Dragon Pulse
- Shadow Ball

Expected:
- grade color is readable but restrained
- Pokemon sprites retain silhouette/color readability
- grade fully restores after the animation

### Weather
Test:
- Rain Dance + rain turn
- Sunny Day + sun turn
- Sandstorm + sandstorm turn
- Hail + hail turn

Expected:
- initiation and end-of-turn presentation use the same visual identity
- no visible color-pop mismatch between the move and subsequent weather tick
- weather particles remain readable over the arena grade

### No-change controls
Spot-check:
- Thunder
- Psychic
- Surf
- Dark Void
- Judgment

Expected:
- they still look complete next to the upgraded moves
- if they do, leave them unchanged

## Battle HUD
Check:
- player/enemy healthbox navy/slate chrome reads clearly
- HP-state colors remain immediately recognizable
- status colors remain distinct
- text/highlights remain crisp
- cursor remains readable against all battle backgrounds

## Defect recording

For each issue record:
- location or move
- time of day/weather if applicable
- screenshot
- exact visual problem
- whether it is reproducible
- severity:
  - blocking: navigation/readability/resource failure
  - major: obvious presentation defect
  - minor: subjective polish only

Only blocking/major issues should reopen Pass G source work by default.
Minor taste adjustments should be grouped and reviewed together to avoid endless palette churn.

## Exit

Pass G is ready to merge when:
- repository CI is green
- no blocking/major Delta visual defect is found
- any accepted fixes have been revalidated
