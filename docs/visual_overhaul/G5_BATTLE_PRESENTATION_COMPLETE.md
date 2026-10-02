# G5 Battle Presentation — Source-Side Completion

Status: **source-side complete**

G5 upgrades battle presentation while preserving Platinum's battle renderer, battle-script runtime,
resource formats, gameplay logic, and existing move timing contracts.

## Completed scope

### Battle HUD
- refreshed normal player/enemy healthbox chrome through the existing shared palette path
- retained HP-state, status, white-highlight, and black readability colors
- refreshed the battle command cursor without changing its cell/animation contract
- Safari healthbox remains deliberately separate because it owns an independent palette contract

### Battle backgrounds
- completed reproducible palette treatment for common natural terrain families
- completed special-arena treatment for indoor, Giratina, Elite Four, and Champion arenas
- completed Battle Frontier palette treatment
- preserved terrain geometry, indexed pixel maps, cell data, animation data, and archive ordering

### Weather presentation
- aligned Rain Dance / Sunny Day / Sandstorm / Hail initiation grades with their shared end-of-turn
  weather animation paths
- preserved weather mechanics, duration, damage, particles, sounds, and turn sequencing

### Reusable impact/staging language
G5 uses Platinum's existing `Func_ShakeBg(..., SHAKE_BG_TARGET_BASE)` path as a selective
base-arena reaction layer.

The rule is intentionally narrow:
- arena motion is added only at explicit impact frames
- strength scales with the implied weight of the move
- existing battler shake and effect-background shake remain independent
- no global damage shake is introduced
- donor research may justify a no-change decision

### Scene-grade identity
Existing `Func_FadeBg` scene grades were specialized where Platinum already had the correct
structure but used generic black:
- Aura Sphere — dark blue
- Energy Ball — teal green
- Flash Cannon — dark gray
- Dragon Pulse — dark purple

Shadow Ball gained only a restrained dark-purple base-arena grade; its native particles, timing,
sound, and defender treatment remain intact.

## Selective move-impact upgrades

The source-side move staging pass includes:
- Body Slam
- Giga Impact
- Explosion
- Stone Edge
- Close Combat
- Brave Bird
- Earthquake
- Hyper Beam
- Dragon Rush
- Rock Slide
- Fire Blast
- Hydro Pump
- Blizzard
- Draco Meteor
- Leaf Storm
- Overheat
- Focus Blast
- Solar Beam
- Spacial Rend
- Roar of Time
- Seed Flare
- Flare Blitz
- Wood Hammer
- Head Smash
- Superpower
- Hammer Arm
- Volt Tackle
- Double-Edge
- Megahorn
- Meteor Mash
- Cross Chop
- Blast Burn
- Hydro Cannon
- Frenzy Plant
- Psycho Boost
- Sacred Fire

Each edit retains the move's existing particle resources, sound sequence, gameplay effect,
and primary animation structure.

## Explicit no-change controls

Research/auditing also locked important no-change decisions where Platinum already has sufficient
presentation:
- Thunder
- Psychic
- Ice Beam
- Flamethrower
- Thunderbolt
- Shadow Force
- Dark Void
- Judgment
- Waterfall
- Aqua Tail
- Outrage
- Dragon Claw
- Iron Head
- Poison Jab
- Eruption
- Water Spout
- Doom Desire
- Aeroblast
- Dark Pulse
- Earth Power
- Power Gem
- Sludge Bomb
- Bug Buzz
- Surf
- Water Pulse
- Signal Beam
- Magma Storm
- Crush Grip
- Luster Purge
- Mist Ball
- Lunar Dance
- Attack Order
- Defend Order
- Heal Order

These controls are part of the pass, not omissions. They prevent the new scene-wide language from
becoming a generic effect applied to every strong move.

## Donor policy

Emerald, Yellow, Stadium/Stadium 2, and PMD Sky were used as technique/reference sources.
No donor battle particles, backgrounds, cameras, sprites, or move-animation resources were imported.

The retained rule is:
> borrow presentation language, not incompatible renderer assets.

## Validation

Current objective gates for the G5 source tree:
- visual formatting: passing
- visual asset export: passing
- PR lint: passing
- normal US Rev 0 / Rev 1 ROM builds: passing

The G4 runtime-symbol harness is an environment/runtime QA gate rather than a G5 battle-animation
dependency. Its most recent unrelated failure was an external Metroskrew download failure on one
matrix leg; that job was re-run rather than treated as a source regression.

## Remaining review

G5 does not require additional source expansion before G6.

A Delta rendered-frame review remains useful for subjective tuning of:
- shake strength
- scene-grade intensity
- special-arena palette taste
- HUD palette taste

Those are polish checks. Objective source integration is closed unless runtime review identifies a
specific defect.

## Next

Proceed to **G6 — Showcase Integration & Final Visual Polish**, using:
1. Eterna Forest
2. Snowpoint / Route 217
3. Distortion World

as primary quality benchmarks, followed by Spear Pillar, Galactic interiors, lakes, and Turnback Cave.
