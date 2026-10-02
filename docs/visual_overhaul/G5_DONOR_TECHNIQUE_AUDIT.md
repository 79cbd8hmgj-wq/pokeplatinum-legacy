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


## Legendary-signature staging batch

The same native staging rule was applied to three signature attacks whose Platinum scripts already
have strong bespoke scene treatment but lacked a distinct base-arena reaction on the decisive hit:

- Spacial Rend — adds a restrained base-arena jolt under the defender impact while preserving its switched background and existing effect-background shake.
- Roar of Time — adds the strongest base-arena response in this batch at the white-flash impact, without changing its charge/fade sequence.
- Seed Flare — keeps its existing white scene flash and effect-background motion, with a separate restrained base-arena reaction on the defender hit.

No-change controls:
- Shadow Force — already has grayscale staging, attacker disappearance/reappearance, timed sound, and defender impact treatment.
- Dark Void — already uses a dedicated moving background, projection change, layered particles, and battler motion.
- Judgment — already uses a full white scene grade plus repeated defender-impact shakes; additional arena motion was not justified.

No particles, sounds, backgrounds, timing, battler visibility logic, or donor assets were replaced.

## Heavy physical-collision staging batch

The same base-arena impact layer was extended to a narrow group of high-power physical attacks whose
native scripts already communicate a large collision but leave most of the motion on the defender or
effect background:

- Flare Blitz — short base-arena jolt at the defender collision after the attacker rush.
- Wood Hammer — adds a separate base-arena impact beneath its existing effect-background shake.
- Head Smash — receives the strongest base-arena jolt in this batch while preserving its switched background.
- Superpower — adds a heavy arena reaction beneath the existing defender shake and attacker movement.
- Hammer Arm — adds a restrained base-arena response beneath its existing effect-background movement and defender squash.

No-change controls:
- Waterfall — its moving dedicated background, attacker motion, defender fade, and shake already create sufficient scene motion.
- Aqua Tail — retained as a cleaner mid-power physical Water strike rather than escalating every contact move.
- Outrage — already uses a moving switched background, repeated full-scene red pulses, and sustained defender shake.
- Dragon Claw, Iron Head, and Poison Jab — deliberately remain localized mid-power impacts rather than inheriting heavyweight arena motion.

This keeps base-arena movement proportional to move weight instead of turning it into a universal damage effect.

## Legacy ultimate/signature staging batch

A final high-power legacy/signature sweep applies the same native base-arena reaction rule to moves
whose existing scripts already provide large bespoke effects but leave the decisive impact mostly
localized to the defender/effect background:

- Blast Burn — adds a heavy base-arena jolt to both attacker-side branches at the final defender impact.
- Hydro Cannon — adds a heavy base-arena response beneath the sustained defender shake.
- Frenzy Plant — adds a heavy arena reaction when the delayed vine strike lands.
- Psycho Boost — adds a restrained-but-distinct base-arena reaction beneath the defender impact.
- Sacred Fire — adds a restrained base-arena jolt beneath the existing switched-background hit.

No-change controls:
- Eruption — already combines a full dark-red scene grade, repeated eruption emitters, effect-background motion, multi-target defender grades, and long defender shakes.
- Water Spout — retained around its broad multi-target water burst and sustained defender shake rather than adding more scene motion.
- Doom Desire — its delayed hit already owns a full white scene treatment plus a long defender-impact sequence.
- Aeroblast — already uses a dedicated switched background with a long background shake and defender impact.

No particle resources, backgrounds, sounds, timing, power/effect logic, or donor assets were changed.

## Generic special-attack control audit

A final control sweep checked several common special attacks after the scene-grade and impact pilots.
No edits were justified:

- Dark Pulse — already uses background grayscale, dedicated attacker-side effects, defender shake, and a dark-purple defender grade.
- Earth Power — already combines a dark-red arena grade with three large particle/impact waves and repeated background/defender shake.
- Power Gem — already uses a full base-scene fade, a long jewel buildup, and sustained defender shake; extra grading would mostly duplicate its native presentation.
- Sludge Bomb — the parabolic projectile, layered impact emitters, purple defender grade, and localized hit language are appropriate for a normal high-power Poison attack.
- Bug Buzz — its multi-emitter sound field and defender shake already read clearly without heavyweight arena movement.
- Surf — already owns a dedicated scrolling background plus multi-target particles, color treatment, and broad battler shake.
- Water Pulse — already uses a moving switched background, staged pulse field, projectile travel, defender shake, and cyan impact grade.
- Signal Beam — all normal, friendly-fire, and contest branches already combine sustained sprite shake with repeated red/green color pulses.

These no-change rulings are intentional. G5 should not turn every damaging move into a scene-wide effect.

## Donor-control comparison: common special attacks

Emerald was used only as a presentation reference for several common special attacks.

Findings:
- Psychic — Platinum already uses a dedicated moving background plus attacker/defender treatment; no change.
- Ice Beam — Platinum already uses a cool base-background grade plus defender shake; no change.
- Flamethrower — Platinum already combines a dark-red arena grade with sustained attacker/defender shake; no change.
- Thunderbolt — Platinum already combines a darkened arena, repeated electrical beats, defender flash, and defender shake; no change.
- Shadow Ball — Platinum had the projectile, defender shake, and defender purple fade, but lacked the broader scene treatment seen in Emerald's dedicated ghost background. Added only a restrained native dark-purple base-background grade and restore.

This comparison is intentionally conservative: donor research is allowed to justify leaving Platinum unchanged when its native presentation already expresses the same idea well.


## Native scene-grade identity batch

Emerald's scripts frequently treat palette/background grading as a separate presentation layer from
particles and battler motion. Platinum already exposes that idea directly through `Func_FadeBg`,
so the next pass keeps every native particle/timing path intact and changes only the color used by
existing arena fades.

Updated:
- Aura Sphere — black -> dark blue
- Energy Ball — black -> teal green
- Flash Cannon — black -> dark gray
- Dragon Pulse — black -> dark purple

These are not donor asset conversions. They are Platinum-native color-language changes informed by
cross-game research into how strong attacks separate scene atmosphere from their primary particle effect.
