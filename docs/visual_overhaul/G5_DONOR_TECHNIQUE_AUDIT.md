# G5 Battle Presentation — Donor Technique Audit

## Policy

External repositories are research sources first. This audit does not authorize asset transplantation.

A donor asset is eligible only when its Platinum resource contract is already known and transfer is trivial, deterministic, reproducible, and build-verifiable. Otherwise the donor is used only for presentation ideas.

## Research findings

### Pokemon Emerald — technique reference

The Emerald battle-animation command surface explicitly separates:
- battle-platform shake
- palette/screen tint
- background swaps/fades
- visual tasks
- sound timing
- sprite/particle sequencing

Useful idea for Platinum:
- treat arena movement as a distinct layer from battler shake
- synchronize short environment movement with the actual impact frame
- use color grading and background treatment to reinforce elemental identity
- preserve particle/sound timing instead of increasing every effect simultaneously

Classification: **Technique**.

### Pokemon Yellow — historical presentation reference

Yellow's battle animation engine applies different screen-shake profiles for different damage presentations and uses timed flashes for specific moves such as Rock Slide, Explosion/Selfdestruct, and Blizzard.

Useful idea for Platinum:
- impact motion should be event-specific rather than globally uniform
- repeated-hit or sustained-force moves can use multiple restrained pulses
- flashes/shakes should occur on explicit impact beats, not continuously

Classification: **Reference / Technique**.

### Pokemon Stadium / Stadium 2 — staging reference

The Stadium projects remain useful primarily for battle framing, anticipation, recovery, and the sense that the arena reacts to high-force attacks. Their renderer/camera systems are not direct DS donors.

Useful idea for Platinum:
- create stronger attack anticipation and recovery through Platinum-native battler/background motion
- reserve larger scene motion for attacks whose existing animation already implies major physical force

Classification: **Reference**.

### Pokemon Mystery Dungeon: Explorers of Sky — effects reference

PMD Sky exposes a dedicated move/effect animation architecture and remains useful for layered effect pacing and environmental atmosphere. Its dungeon/effect engine is not a Platinum transplant target.

Useful idea for Platinum:
- layer effects by timing and role rather than by simply adding more sprites
- keep a clear primary action, impact beat, and recovery

Classification: **Technique / Reference**.

## G5 implementation rule derived from research

For the current Platinum branch:

1. keep Platinum's existing particle resources and move-specific backgrounds;
2. use `Func_ShakeBg(..., SHAKE_BG_TARGET_BASE)` as the DS-native equivalent of arena/platform reaction;
3. preserve existing battler shake independently;
4. add motion only at explicit impact beats;
5. prefer one or two restrained pulses over continuous full-screen movement;
6. do not import donor sprites, backgrounds, particles, or camera assets for this pass.

## First donor-informed elemental-force pilot

Apply the rule to:
- Fire Blast — short base-arena jolt when the defender impact/fire burst lands
- Hydro Pump — stronger directional base-arena reaction under the pressure impact
- Blizzard — two restrained base-arena pulses aligned with its existing two defender-shake beats

Thunder is retained as a control because Platinum already gives it a base-background shake plus an effect-background flash.

## Second donor-informed signature-impact batch

The same technique policy was extended only to moves whose existing Platinum animation already
contains a large effect/background sequence and a clearly defined impact beat:

- Draco Meteor — only the final meteor impact now moves the base arena; earlier effect-background pulses remain unchanged
- Leaf Storm — adds a restrained arena reaction under the defender impact
- Overheat — adds a short arena jolt at the defender heat burst
- Focus Blast — adds a compact arena reaction when the projectile lands
- Solar Beam — adds a restrained horizontal arena response only on the firing branch; the charge branch is unchanged

These are script-only additions using Platinum's existing `Func_ShakeBg` primitive. No donor assets,
particle resources, sounds, backgrounds, or animation data were imported.


## Donor-control comparison: common special attacks

Emerald was used only as a presentation reference for several common special attacks.

Findings:
- Psychic — Platinum already uses a dedicated moving background plus attacker/defender treatment; no change.
- Ice Beam — Platinum already uses a cool base-background grade plus defender shake; no change.
- Flamethrower — Platinum already combines a dark-red arena grade with sustained attacker/defender shake; no change.
- Thunderbolt — Platinum already combines a darkened arena, repeated electrical beats, defender flash, and defender shake; no change.
- Shadow Ball — Platinum had the projectile, defender shake, and defender purple fade, but lacked the broader scene treatment seen in Emerald's dedicated ghost background. Added only a restrained native dark-purple base-background grade and restore.

This comparison is intentionally conservative: donor research is allowed to justify leaving Platinum unchanged when its native presentation already expresses the same idea well.
