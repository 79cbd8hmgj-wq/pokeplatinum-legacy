"""Hand-authored (provisional) animation recipes for the 33 B9 P1/P2 moves.

Every recipe = one PRIMARY + up to two ALTERNATIVES.  A recipe names the native Platinum layer it keeps, other Platinum particle emitters it
borrows, installed Opal FX sheets it reuses (zero new tiles), new sheets built from donor cells (cell numbers are the board cells of
``MOVE_CANDIDATE_MATRIX``), and the Opal cues it plays.  Timing is symbolic: anchor ``L`` = script start, ``H`` = the native hit beat
(first defender emitter, else the last emitter start - see ``native_scripts``), offsets/lengths in 60 fps frames.
``recipes.py`` resolves and VALIDATES everything (cell exists and was not judged wrong/illegible, installed sheet+sequence exists, <= 2 sprite
managers live, <= 400 concurrent OBJ tiles, <= 40 concurrent OAM, <= 192 tiles per new sheet, cadence vs native) and fails on a violation.

Nothing here is an implementation or an approval: every selection is PROVISIONAL until it is built, run in an emulator and accepted.
Design basis (owner decisions): native Platinum emitters and new Opal sequences are used together wherever strongest; no donor game's look is
privileged - assets are combined across libraries by quality and cohesion; weak moves (Double Team, Hypnosis, Swords Dance) get custom composites.
"""
from __future__ import annotations


def N(emitters, note=""):                      # keep (some of) the native script's own emitters, unchanged
    return {"role": "native", "kind": "native_keep", "emitters": emitters, "note": note}


def NB(spa, at, note, emitters=None):          # borrow another Platinum move's emitters (second particle resource slot)
    return {"role": "borrow", "kind": "native_borrow", "spa": spa, "emitters": emitters, "at": at, "len": 40, "note": note}


def S(role, sheet, seq, at, ln, macro, n=1, variant=None, note=""):   # installed Opal FX sheet (zero new tiles)
    return {"role": role, "kind": "sheet", "sheet": sheet, "seq": seq, "at": at, "len": ln, "macro": macro, "n": n, "variant": variant, "note": note}


def D(role, cells, at, ln, macro, n=1, note="", tint=None):          # new donor-derived sheet part (board cell numbers of this move, or full asset ids)
    return {"role": role, "kind": "donor", "cells": cells if isinstance(cells, list) else [cells], "at": at, "len": ln, "macro": macro, "n": n, "note": note, "tint": tint}


def Q(role, macro, at, note="", ln=0):                               # cue without art
    return {"role": role, "kind": "cue", "macro": macro, "at": at, "len": ln, "note": note}


def X(title, how):                                                   # free-text design requirement for a custom composite (not costed art)
    return {"role": "composite", "kind": "design_note", "title": title, "note": how, "at": ("L", 0), "len": 0}


def V(name, strategy, summary, parts, why):
    return {"name": name, "strategy": strategy, "summary": summary, "parts": parts, "why": why}


L, H = "L", "H"
WIND, RING, STRIKE, ROCK, NATURE = "opal_b9_wind", "opal_fx_ring", "opal_b9_strike", "opal_b9_rock", "opal_b9_nature"

RECIPES = {
 # ------------------------------------------------------------------------------------------------------------------ P1
 "Headbutt": {"primary": V("Skull-first slam", "native+opal", "Keep the native burst/star masks; add a ground puff on the lunge, a Ranger 2 ring-burst plus Emerald starburst on the hit, a gold ring and heavy recoil, then dizzy stars.",
     [N([0, 1], "native burst + star masks at the hit"), S("launch", WIND, "puff", (L, 0), 8, "OpalFx ... OPAL_B9_WIND_SEQ_PUFF (feet)", note="dust under the attacker as it winds up"),
      D("impact", [10, 7], (H, 0), 12, "OpalImpactBurst x2 (ring-burst, starburst 130%)", note="Ranger 2 ef014 ring + fireball burst; Emerald impact.png starburst"),
      S("impact", RING, "ring_expand", (H, 0), 12, "OpalReactHeavy (ring + heavy shake + camera punch)", variant="gold"),
      D("aftermath", [2], (H, 2), 20, "OpalResidual (drifting stars over the defender)", note="Emerald gold_stars.png")],
     "Heavy-contact template (weight transfer, compressed impact burst, recovery); the hit beat stays on the native frame so cadence is unchanged."),
  "alts": [V("Light thud", "opal_existing", "Zero new art: existing strike flash + gold ring + light recoil.", [N([0, 1]), S("launch", WIND, "puff", (L, 0), 8, "OpalFx puff"), S("impact", STRIKE, "hit_small", (H, 0), 10, "OpalImpactBurst"), S("impact", RING, "ring_expand", (H, 0), 12, "OpalImpactBurst", variant="gold"), Q("cue", "OpalReactLight", (H, 0))], "Cheapest and closest to the P0 contact language."),
           V("Ranger ring-burst", "native+donor", "A bigger, explosive hit from a Ranger 2 ring + fireball cell and sparkle aftermath.", [N([0, 1]), D("impact", [10], (H, 0), 14, "OpalImpactBurst scale 120"), D("aftermath", [15], (H, 4), 22, "OpalResidual"), Q("cue", "OpalCamPunchHeavy", (H, 0))], "Bolder silhouette for a signature Headbutt; larger tile cost.")]},
 "Slam": {"primary": V("Shockwave drop", "native+opal", "Native radial/spike masks, a red-yellow directional strike plus starburst on the hit, rock-sheet break and dirt at the feet, heavy camera punch.",
     [N([0, 1]), D("impact", [6, 7], (H, 0), 10, "OpalImpactBurst x2", note="Emerald horn_hit.png (down-strike) + impact.png"),
      S("aftermath", ROCK, "break", (H, 2), 13, "OpalImpactBurst (ground)", n=2), S("aftermath", ROCK, "dirt", (H, 4), 10, "OpalResidual", n=3), Q("cue", "OpalCamPunchHeavy", (H, 0)), Q("cue", "OpalReactLight", (H, 0))],
     "Heavier-than-Headbutt: ground debris and a heavy camera punch sell the weight; all cues hang off the native hit frame."),
  "alts": [V("Existing-only slam", "opal_existing", "Strike flash + earth ring, no new art.", [N([0, 1]), S("impact", STRIKE, "hit_small", (H, 0), 10, "OpalImpactBurst", n=2), S("impact", RING, "flat_expand", (H, 2), 14, "OpalReactHeavy", variant="earth")], "Zero-tile fallback."),
           V("Debris slam", "native+opal", "Rock-sheet shards and dust around the hit.", [N([0, 1]), S("impact", ROCK, "shards", (H, 0), 15, "OpalImpactBurst"), S("aftermath", ROCK, "dirt", (H, 4), 12, "OpalResidual", n=2), Q("cue", "OpalCamPunchHeavy", (H, 0))], "Reuses the P0 rock vocabulary.")]},
 "Wing Attack": {"primary": V("Crescent sweep", "native+opal", "Native feather masks; installed wind crescents sweep to the target alongside white feather / air-slash trails from Emerald art, with a light recoil on the hit.",
     [N([0, 1]), S("travel", WIND, "crescent", (L, 2), 24, "OpalProjectile (trail, arc 6)", n=2), D("travel", [7, 6], (L, 6), 16, "OpalProjectile (trail, arc 6)", n=2, note="Emerald white_feather.png + air_slash.png"),
      Q("cue", "OpalReactLight", (H, 0))],
     "Wing-strike template: wing arcs, displaced air, then impact; the crescents reuse the installed wind sheet so the sweep matches Gust/Quick Attack, the feathers add the wing identity."),
  "alts": [V("Existing wind", "opal_existing", "Wind crescent + streaks and a hit flash from installed sheets.", [N([0, 1]), S("travel", WIND, "crescent", (L, 4), 20, "OpalProjectile", n=2), S("impact", STRIKE, "hit_small", (H, 0), 10, "OpalImpactBurst"), Q("cue", "OpalReactLight", (H, 0))], "Zero new tiles."),
           V("Cyan blade wings", "native+donor", "Ranger 2 cyan blade streak for a harder, brighter wing slice.", [N([0, 1]), D("travel", [9], (L, 6), 14, "OpalProjectile", n=2), NB("slash", (H, 0), "slash flash masks"), Q("cue", "OpalReactLight", (H, 0))], "More aggressive look.")]},
 "Aerial Ace": {"primary": V("Double cut", "native+opal", "Native four-emitter cut at frame 15; add dash lines and a cyan blade streak ahead of it and a mirrored double claw-cut flash on the hit.",
     [N([0, 1, 2, 3]), D("travel", [6, 10], (L, 0), 15, "OpalProjectile (trail)", n=2, note="Emerald blue_lines.png + Ranger 2 ef010 cyan blade streak"),
      S("impact", STRIKE, "claw_a", (H, 0), 10, "OpalImpactBurst"), S("impact", STRIKE, "claw_b", (H, 3), 10, "OpalImpactBurst"), Q("cue", "OpalReactLight", (H, 0))],
     "Speed-contact template (afterimage, short dash, impact); the second cut lands 3 frames after the first for the 'double' read."),
  "alts": [V("Existing wind cut", "opal_existing", "Wind streak lead-in + strike claw cuts.", [N([0, 1, 2, 3]), S("travel", WIND, "streak", (L, 0), 15, "OpalProjectile", n=2), S("impact", STRIKE, "claw_a", (H, 0), 10, "OpalImpactBurst"), S("impact", STRIKE, "claw_b", (H, 3), 10, "OpalImpactBurst")], "Zero new tiles."),
           V("PMD streak cuts", "native+donor", "PMD Sky white cut lines for crisp speed slashes.", [N([0, 1, 2, 3]), D("impact", [5, 2], (H, 0), 12, "OpalImpactBurst", n=2), Q("cue", "OpalReactLight", (H, 0))], "Crisp, graphic read; large PMD tile cost (needs splitting).")]},
 "Spark": {"primary": V("Charge-and-jump", "native+opal", "Native discharge emitters; thunder-orb charge aura on the user, orange zig-zag arcs travelling to the target, spark burst, yellow light pulse.",
     [N([0, 1, 2, 3]), S("launch", "opal_thunder", "orb", (L, 0), 12, "OpalChargeAura"), D("travel", [7], (L, 8), 12, "OpalProjectile (trail)", n=2, note="Emerald spark_1.png"),
      S("impact", "opal_thunder", "sparks", (H, 0), 12, "OpalImpactBurst"), Q("cue", "OpalLightPulse yellow", (H, 0)), Q("cue", "OpalReactLight", (H, 0))],
     "Electric-contact template: charging aura into impact; reuses the B2 thunder sheet so the look matches Thunder Shock/Thunderbolt."),
  "alts": [V("Existing thunder", "opal_existing", "Installed thunder sheet only.", [N([0, 1, 2, 3]), S("launch", "opal_thunder", "orb", (L, 0), 12, "OpalChargeAura"), S("impact", "opal_thunder", "bolt", (H, 0), 13, "OpalImpactBurst")], "Zero new tiles."),
           V("Sparkle crackle", "native+donor", "Ranger 2 yellow sparkles as residual crackle.", [N([0, 1, 2, 3]), S("launch", "opal_thunder", "orb", (L, 0), 12, "OpalChargeAura"), D("aftermath", [10], (H, 2), 20, "OpalResidual")], "Adds residual sparkle.")]},
 "Flame Wheel": {"primary": V("Rolling fire ring", "native+opal", "Keep native emitters and the already-installed Ranger fire-bloom sprite; add an ember trail along the dash, an Opal flame tongue on the hit and an orange light pulse.",
     [N([0, 1, 2], "native wheel + bloom"), S("travel", "opal_b9_ember", "ember", (H, -16), 16, "OpalProjectile (trail)", n=3, note="ember trail along the native 24-px dash"),
      S("impact", "opal_fire", "tongue", (H, 0), 11, "OpalImpactBurst"), Q("cue", "OpalLightPulse orange", (H, 0)), Q("cue", "OpalReactLight", (H, 0))],
     "Fire-contact template (fire orbit, forward roll, cinders). The native script already carries a Ranger 2 donor sprite, so this stays within a known-good donor mix."),
  "alts": [V("Ember only", "opal_existing", "Ember trail + pop only.", [N([0, 1, 2]), S("travel", "opal_b9_ember", "ember", (H, -16), 16, "OpalProjectile", n=3), S("impact", "opal_b9_ember", "ember_pop", (H, 0), 8, "OpalImpactBurst")], "Cheapest."),
           V("Spiral flame ring", "native+donor", "A recoloured PMD spiral disc rotating around the user as a 'wheel', plus ember trail.", [N([0, 1, 2]), D("launch", [10], (L, 0), 24, "OpalChargeAura (spiral, scale growth)", note="PMD effect.bin#128 recoloured to the fire ramp"), S("travel", "opal_b9_ember", "ember", (H, -16), 16, "OpalProjectile", n=3)], "Gives the 'wheel' an explicit rotating shape.")]},
 "Aqua Jet": {"primary": V("Water-wrapped dash", "native+opal", "Native emitters; a water column wraps the dash, a Ranger 2 spray fan and Opal foam burst on the hit, droplets after.",
     [N([0, 1, 2, 3, 4, 5], "native aqua jet emitters"), S("travel", "opal_water", "column", (L, 0), 16, "OpalProjectile (trail)"), D("impact", [4], (H, 0), 12, "OpalImpactBurst", note="Ranger 2 e052 blue-white spray fan"),
      S("impact", "opal_water", "foam", (H, 0), 6, "OpalImpactBurst"), S("aftermath", "opal_water", "droplet", (H, 3), 24, "OpalResidual", n=3), Q("cue", "OpalReactLight", (H, 0))],
     "Water-contact template (water cocoon, charge, splash). Reuses the B2 water sheet; the new spray fan adds a directional splash."),
  "alts": [V("Existing water", "opal_existing", "Column + foam + droplets.", [N([0, 1, 2, 3, 4, 5]), S("travel", "opal_water", "column", (L, 0), 16, "OpalProjectile"), S("impact", "opal_water", "foam", (H, 0), 6, "OpalImpactBurst"), S("aftermath", "opal_water", "droplet", (H, 3), 24, "OpalResidual", n=3)], "Zero new tiles."),
           V("Pulse bubble", "native+opal", "Borrowed Water Pulse sphere/droplet emitters with Opal foam.", [N([0, 1, 2, 3, 4, 5]), NB("water_pulse", (H, 0), "glossy bubble sphere + droplets"), S("impact", "opal_water", "foam", (H, 0), 6, "OpalImpactBurst")], "Glossier water.")]},
 "BubbleBeam": {"primary": V("Dense bubble stream", "native+opal", "Native stream; three staggered bubble lanes of two sizes, a ripple ring and pop burst on arrival.",
     [N([0]), S("travel", "opal_b9_bubble", "bubble", (L, 0), 40, "OpalProjectile (lanes at 0/6/12)", n=3), S("travel", "opal_b9_bubble", "bubble_small", (L, 3), 40, "OpalProjectile", n=3),
      D("impact", [9], (H, 0), 15, "OpalImpactBurst", note="PMD effect.bin#183 ring + dots as ripples"), S("impact", "opal_b9_bubble", "pop_big", (H, 0), 13, "OpalImpactBurst"), Q("cue", "OpalReactLight", (H, 0))],
     "Water-bubble template (slow varied bubbles, collision, pop and ripples)."),
  "alts": [V("Bubble sheet only", "opal_existing", "P0 bubble sheet at higher density.", [N([0]), S("travel", "opal_b9_bubble", "bubble", (L, 0), 40, "OpalProjectile", n=4), S("impact", "opal_b9_bubble", "pop", (H, 0), 12, "OpalImpactBurst", n=3)], "Zero new tiles."),
           V("Glossy bubbles", "native+opal", "Borrowed Bubble emitters (glossy sphere) plus foam.", [N([0]), NB("bubble", (L, 0), "glossy bubble spheres"), S("impact", "opal_water", "foam", (H, 0), 6, "OpalImpactBurst")], "Native-look bubbles.")]},
 "Magical Leaf": {"primary": V("Homing curved leaves", "native+opal", "Native leaf waves; hero leaf from Ranger 2 shaded art on curved arcs with Opal leaf spins, razor glint and flutter on arrival.",
     [N([0, 1, 2], "native leaf waves at 0/80/160"), S("travel", NATURE, "leaf_spin", (L, 0), 34, "OpalProjectile (arc 8)", n=3), D("travel", [9], (L, 4), 34, "OpalProjectile (arc 10)", n=2, note="Ranger 2 e079 shaded leaves"),
      S("impact", NATURE, "razor_blade", (H, 0), 12, "OpalImpactBurst"), S("aftermath", NATURE, "leaf_flutter", (H, 4), 24, "OpalResidual", n=3), Q("cue", "OpalReactMagic green", (H, 0))],
     "Leaf-homing template (offset launch, curved travel, convergence); the shaded Ranger leaf adds a hero projectile over the P0 leaf vocabulary."),
  "alts": [V("Existing nature", "opal_existing", "Installed leaf spin + flutter.", [N([0, 1, 2]), S("travel", NATURE, "leaf_spin", (L, 0), 34, "OpalProjectile", n=4), S("aftermath", NATURE, "leaf_flutter", (H, 4), 24, "OpalResidual", n=3)], "Zero new tiles."),
           V("Blade leaves", "native+opal", "Borrowed Leaf Blade emitters for sharper leaves.", [N([0, 1, 2]), NB("leaf_blade", (L, 0), "leaf silhouettes"), S("impact", NATURE, "razor_blade", (H, 0), 12, "OpalImpactBurst")], "Sharper silhouette.")]},
 "Metal Claw": {"primary": V("Steel rake", "native+opal", "The native script is sprite-based (no particles); keep its claw sprite and add steel-tinted claw swipes, a four-point metal glint and a light recoil.",
     [N([], "native claw sprite flow (no particle archive)"), S("travel", STRIKE, "claw_a", (L, 2), 10, "OpalImpactBurst (steel palette variant)", note="needs a steel palette variant of the strike sheet"), S("travel", STRIKE, "claw_b", (L, 5), 10, "OpalImpactBurst"),
      D("impact", [0], (H, 0), 10, "OpalImpactBurst x2", n=2, note="Emerald sparkle_6.png glint"), Q("cue", "OpalReactLight", (H, 0))],
     "Steel-slash template (metal glint, trailing slash). Platinum has no particle for this move, so Opal carries the effect."),
  "alts": [V("Donor claw swipes", "native+donor", "Emerald claw_slash.png swipes + glint.", [N([]), D("travel", [5], (L, 2), 14, "OpalImpactBurst", n=3), D("impact", [0], (H, 0), 10, "OpalImpactBurst")], "Distinct claw drawing."),
           V("Slash flash", "native+opal", "Borrowed Slash flash masks + glint.", [N([]), NB("slash", (L, 2), "slash flash masks"), D("impact", [0], (H, 0), 10, "OpalImpactBurst")], "Native-look slashes.")]},
 "Rock Tomb": {"primary": V("Converging boulders", "native+opal", "Native falling rocks (30-60 frame cadence); Opal boulder, break and dirt at each landing plus residual dust.",
     [N([1, 0], "native rock falls"), S("travel", ROCK, "boulder", (L, 28), 14, "OpalProjectile (fall)", n=3), S("impact", ROCK, "break", (H, 0), 13, "OpalImpactBurst", n=2), S("aftermath", ROCK, "dirt", (H, 2), 20, "OpalResidual", n=3), Q("cue", "OpalCamPunch", (H, 0))],
     "Rock-fall template (telegraph, staggered fall, dust settle); reuses the P0 rock sheet."),
  "alts": [V("Camera-light tomb", "opal_existing", "Rock sheet only, no camera cue.", [N([1, 0]), S("impact", ROCK, "break", (H, 0), 13, "OpalImpactBurst", n=2), S("aftermath", ROCK, "dirt", (H, 2), 20, "OpalResidual", n=3)], "Cheapest."),
           V("Stone spikes", "native+opal", "Borrowed Stone Edge emitters (spikes + boulder) as a rising tomb wall.", [N([1, 0]), NB("stone_edge", (L, 28), "spike/boulder masks"), S("aftermath", ROCK, "dirt", (H, 2), 20, "OpalResidual", n=3)], "Walled-in look.")]},
 "Rock Slide": {"primary": V("Spread slide", "native+opal", "Native three-emitter slide; three boulder lanes spreading across the target side, break/dirt per landing, pebble debris and a camera punch.",
     [N([0, 1, 2]), S("travel", ROCK, "boulder", (L, 0), 40, "OpalProjectile (3 lanes)", n=3), S("impact", ROCK, "break", (H, 0), 13, "OpalImpactBurst", n=3), D("aftermath", [5], (H, 4), 22, "OpalResidual", n=2, note="Ranger 2 e129 pebbles"), Q("cue", "OpalCamPunchHeavy", (H, 0))],
     "Rock-fall (spread) template; heavier camera cue than Rock Tomb to separate the two."),
  "alts": [V("Existing slide", "opal_existing", "Rock sheet only.", [N([0, 1, 2]), S("travel", ROCK, "boulder", (L, 0), 40, "OpalProjectile", n=3), S("impact", ROCK, "break", (H, 0), 13, "OpalImpactBurst", n=3), S("aftermath", ROCK, "dirt", (H, 4), 12, "OpalResidual", n=3)], "Zero new tiles."),
           V("Wrecker debris", "native+opal", "Borrowed Rock Wrecker debris emitters.", [N([0, 1, 2]), NB("rock_wrecker", (H, 0), "debris masks"), S("impact", ROCK, "break", (H, 0), 13, "OpalImpactBurst", n=2)], "More debris.")]},
 "Crunch": {"primary": V("Closing jaws", "native+opal", "Native five-emitter jaw rows; flanking purple fangs, a heavier-scaled snap and light recoil, with a camera punch.",
     [N([0, 1, 2, 3, 4]), D("launch", [9], (L, 0), 12, "OpalFx (closing fangs)", n=2, note="Ranger 2 e020 purple fangs"), S("impact", STRIKE, "jaw_upper", (H, -4), 8, "OpalImpactBurst scale 130"), S("impact", STRIKE, "jaw_lower", (H, -4), 8, "OpalImpactBurst scale 130"),
      S("impact", STRIKE, "hit_small", (H, 0), 10, "OpalImpactBurst"), Q("cue", "OpalCamPunch", (H, 0)), Q("cue", "OpalReactLight", (H, 0))],
     "Bite template, bigger and darker than P0 Bite: purple flanking fangs and a larger snap."),
  "alts": [V("Existing jaws", "opal_existing", "P0 jaw sprites, larger.", [N([0, 1, 2, 3, 4]), S("impact", STRIKE, "jaw_upper", (H, -4), 8, "OpalImpactBurst scale 130"), S("impact", STRIKE, "jaw_lower", (H, -4), 8, "OpalImpactBurst scale 130"), Q("cue", "OpalReactLight", (H, 0))], "Zero new tiles; risks looking like Bite."),
           V("Fang masks", "native+opal", "Borrowed Bite/Thunder Fang jaw masks.", [N([0, 1, 2, 3, 4]), NB("thunder_fang", (H, -2), "jaw-row masks"), S("impact", STRIKE, "hit_small", (H, 0), 10, "OpalImpactBurst")], "Native-look jaws.")]},
 "Ice Shard": {"primary": V("Shard volley", "native+opal", "Native shard emitters; three icicle lead shards with trails, ice shatter and glints on impact.",
     [N([1, 3, 2, 4, 0]), D("travel", [6], (L, 0), 24, "OpalProjectile (trail)", n=3, note="Emerald icicle_spear.png"), D("impact", [7], (H, 0), 12, "OpalImpactBurst", n=3, note="Emerald ice_crystals_2.png"),
      S("impact", "opal_ice", "shatter", (H, 0), 12, "OpalImpactBurst"), S("aftermath", "opal_ice", "glint", (H, 4), 9, "OpalResidual", n=3), Q("cue", "OpalReactLight", (H, 0))],
     "Ice-projectile template (crystalline shards, sharp burst); joins the B2 ice sheet."),
  "alts": [V("Existing ice", "opal_existing", "Shatter + glint only.", [N([1, 3, 2, 4, 0]), S("impact", "opal_ice", "shatter", (H, 0), 12, "OpalImpactBurst", n=2), S("aftermath", "opal_ice", "glint", (H, 4), 9, "OpalResidual", n=3)], "Zero new tiles."),
           V("Spear borrow", "native+opal", "Borrowed Icicle Spear emitters.", [N([1, 3, 2, 4, 0]), NB("icicle_spear", (L, 0), "spike masks + ice chunk"), S("impact", "opal_ice", "shatter", (H, 0), 12, "OpalImpactBurst")], "Native-look icicle.")]},
 "Icy Wind": {"primary": V("Frost current", "native+opal", "Native gust emitters; ice-palette wind swirl/streaks to the target and violet-blue crystal drift.",
     [N([0, 1, 2]), S("travel", WIND, "swirl", (L, 0), 40, "OpalProjectile", variant="ice"), S("travel", WIND, "flecks", (L, 10), 50, "OpalResidual (ice flecks)", n=3, variant="ice"), D("aftermath", [6, 7], (H, 4), 24, "OpalResidual", n=3, note="Emerald ice_crystals_4/2")],
     "Ice-wind template (sweeping haze, frost sparkles); uses the existing ice wind palette variant."),
  "alts": [V("Wind ice only", "opal_existing", "Ice-variant wind sheet.", [N([0, 1, 2]), S("travel", WIND, "swirl", (L, 0), 40, "OpalProjectile", variant="ice"), S("aftermath", WIND, "flecks", (H, 0), 40, "OpalResidual", n=3, variant="ice")], "Zero new tiles."),
           V("Powder snow borrow", "native+opal", "Borrowed Powder Snow sparkles.", [N([0, 1, 2]), NB("powder_snow", (H, 0), "snow-crystal sparkle masks"), S("travel", WIND, "swirl", (L, 0), 40, "OpalProjectile", variant="ice")], "Snowier look.")]},
 "Mud Shot": {"primary": V("Clod volley", "native+opal", "Native muddy spray; three brown clods on arcs, droplet splats and a rock-sheet dirt burst on landing.",
     [N([14, 10]), D("travel", [6], (L, 0), 24, "OpalProjectile (arc 8)", n=3, note="Emerald dirt_mound.png"), D("impact", [2], (H, 0), 14, "OpalImpactBurst", n=3, note="Emerald mud_sand_0.png droplets"), S("impact", ROCK, "dirt", (H, 0), 10, "OpalImpactBurst", n=2), Q("cue", "OpalReactLight", (H, 0))],
     "Mud-projectile template (earth splash)."),
  "alts": [V("Existing dirt", "opal_existing", "Rock dirt/shards only.", [N([14, 10]), S("impact", ROCK, "dirt", (H, 0), 10, "OpalImpactBurst", n=3), S("aftermath", ROCK, "shards", (H, 2), 15, "OpalResidual", n=2)], "Zero new tiles."),
           V("Slap splat", "native+opal", "Borrowed Mud-Slap splat masks.", [N([14, 10]), NB("mud_slap", (H, 0), "radial splat + puff masks"), S("impact", ROCK, "dirt", (H, 0), 10, "OpalImpactBurst")], "Native-look splat.")]},
 "Mud Bomb": {"primary": V("Heavy earthen orb", "native+opal", "Native orb + defender emitters; a lobbed boulder-clod orb from Ranger 2 art, splash clods and a heavy camera punch.",
     [N([0, 1, 3, 2]), D("travel", [5], (L, 0), 30, "OpalProjectile (arc 16)", note="Ranger 2 e115 boulders/clods"), D("impact", [7], (H, 0), 14, "OpalImpactBurst", n=3, note="Emerald dirt_mound.png splash"), Q("cue", "OpalCamPunchHeavy", (H, 0)), Q("cue", "OpalReactLight", (H, 0))],
     "Mud-projectile (heavy orb): a single large lobbed mass, not a spray - distinct from Mud Shot."),
  "alts": [V("Existing boulder", "opal_existing", "Rock boulder/dirt.", [N([0, 1, 3, 2]), S("travel", ROCK, "boulder", (L, 0), 30, "OpalProjectile (arc 16)", n=1), S("impact", ROCK, "dirt", (H, 0), 10, "OpalImpactBurst", n=3)], "Zero new tiles."),
           V("Sludge blob", "native+opal", "Borrowed Sludge Bomb blob masks.", [N([0, 1, 3, 2]), NB("sludge_bomb", (H, 0), "soft blob masks"), S("impact", ROCK, "dirt", (H, 0), 10, "OpalImpactBurst", n=2)], "Gloopier.")]},
 "Psybeam": {"primary": V("Colour-pulse beam", "native+opal", "Native pulsing beam; psychic ring pulses and a pink orb travel along it, expanding purple rings and a magenta pulse on the target.",
     [N([0]), S("travel", RING, "ring_expand", (L, 0), 40, "OpalProjectile (3 rings, psychic)", n=3, variant="psychic"), D("travel", [1], (L, 0), 30, "OpalProjectile", n=3, note="Emerald pink_orb.png"), D("impact", [10], (H, 0), 20, "OpalImpactBurst", note="Ranger 2 e041 purple elliptical rings"), Q("cue", "OpalReactMagic magenta", (H, 0))],
     "Psychic-beam template (coloured psychic pulse)."),
  "alts": [V("Ring-only", "opal_existing", "Installed psychic ring palette only.", [N([0]), S("travel", RING, "ring_expand", (L, 0), 40, "OpalProjectile", n=3, variant="psychic"), Q("cue", "OpalReactMagic magenta", (H, 0))], "Zero new tiles."),
           V("Signal borrow", "native+opal", "Borrowed Signal Beam / Psycho Cut masks.", [N([0]), NB("signal_beam", (L, 0), "beam body masks (emitter 0 only: all 9 together peak at ~1,400 quads)", emitters=[0]), S("impact", RING, "ring_expand", (H, 0), 10, "OpalImpactBurst", variant="psychic")], "Beamier.")]},
 "Swift": {"primary": V("Star volley", "native+opal", "Native star emitters; a five-star fan of yellow stars with trails, twinkle glints and a pierce star on arrival.",
     [N([2, 1, 0]), D("travel", [7], (L, 0), 24, "OpalProjectile (5-star fan, trail)", n=5, note="Emerald yellow_star.png"), D("travel", [6], (L, 4), 24, "OpalResidual (twinkles)", n=3, note="Emerald sparkle_6.png"), S("impact", STRIKE, "star_pierce", (H, 0), 8, "OpalImpactBurst", n=2), Q("cue", "OpalLightPulse yellow", (H, 0))],
     "Star-volley template (star trails)."),
  "alts": [V("Existing stars", "opal_existing", "Strike star + wx star pop.", [N([2, 1, 0]), S("impact", STRIKE, "star_pierce", (H, 0), 8, "OpalImpactBurst", n=3), S("aftermath", "opal_fx_wx", "star_pop", (H, 2), 7, "OpalResidual", n=3, variant="gold")], "Zero new tiles."),
           V("Cosmic stars", "native+opal", "Borrowed Cosmic Power star/ring masks.", [N([2, 1, 0]), NB("cosmic_power", (L, 0), "rings + sparkle + star masks"), S("impact", STRIKE, "star_pierce", (H, 0), 8, "OpalImpactBurst")], "More celestial.")]},
 # ------------------------------------------------------------------------------------------------------------------ P2
 "Thunder Wave": {"primary": V("Binding arcs", "native+opal", "Native ring/bolt emitters; thunder-sheet zig-zag arcs wrap the target with Diamond and Emerald arc drawings, flicker and a yellow magic pulse.",
     [N([0, 1, 2]), S("travel", "opal_thunder", "bolt", (L, 0), 13, "OpalProjectile", n=2), D("reaction", [9, 7], (H, 0), 16, "OpalImpactBurst (3 arcs)", n=3, note="Diamond narc_0035 jagged yellow arcs + Emerald spark_2.png zig-zag"), S("reaction", "opal_thunder", "bolt_fade", (H, 4), 8, "OpalResidual", n=2), Q("cue", "OpalReactMagic yellow", (H, 0))],
     "Electric-bind template (arcs wrap the target, brief paralysis flicker)."),
  "alts": [V("Existing thunder", "opal_existing", "Bolt + fade only.", [N([0, 1, 2]), S("travel", "opal_thunder", "bolt", (L, 0), 13, "OpalProjectile", n=2), S("reaction", "opal_thunder", "bolt_fade", (H, 4), 8, "OpalResidual", n=2)], "Zero new tiles."),
           V("Diamond arcs", "native+donor", "Diamond move-effect yellow jagged arcs.", [N([0, 1, 2]), D("reaction", [9], (H, 0), 16, "OpalImpactBurst", n=2), Q("cue", "OpalReactMagic yellow", (H, 0))], "Distinct arc drawing.")]},
 "Hypnosis": {"primary": V("Spiral drowse (custom composite)", "custom_composite", "Native ring emitters + purple fade; a recoloured PMD spiral blooms over the target, psychic rings converge on the eyes, then 'z' glyphs drift up.",
     [N([0, 1, 2, 3, 4], "native rings at L, defender swirl at 30"),
      X("Spiral", "PMD effect.bin#128 is the only true spiral drawing in all pools (red spiral on a disc): recolour to the hypnosis purple/blue ramp, play as an expanding static burst over the defender (scale 60% -> 130%)."),
      D("reaction", ["pmd_sky:files/EFFECT/effect.bin#128"], (H, 0), 30, "OpalImpactBurst (growth, 60% -> 130%)", note="PMD effect.bin#128 spiral, recoloured purple/blue"),
      S("travel", RING, "ring_converge", (H, -12), 14, "OpalProjectile (3 rings -> eyes)", n=3, variant="psychic"), D("aftermath", [1], (H, 12), 30, "OpalResidual (z drift)", n=3, note="Emerald z.png"), Q("cue", "OpalReactMagic purple", (H, 0))],
     "Status-sleep template (spiral and drowse). Composite because no pool has a ready 'hypnosis spiral + z' set."),
  "alts": [V("Rings and z", "opal_existing+donor", "Installed psychic rings + z glyphs only.", [N([0, 1, 2, 3, 4]), S("travel", RING, "ring_converge", (H, -12), 14, "OpalProjectile", n=3, variant="psychic"), D("aftermath", [1], (H, 12), 30, "OpalResidual", n=3)], "Cheap and legible."),
           V("Lullaby", "native+opal", "Borrowed Sing rings + note masks, z glyphs.", [N([0, 1, 2, 3, 4]), NB("sing", (L, 0), "concentric rings + note masks"), D("aftermath", [1], (H, 12), 30, "OpalResidual", n=3)], "Softer, musical.")]},
 "Confuse Ray": {"primary": V("Looping ghost orbs", "native+opal", "Native emitters; three ghost orbs loop around the target on staggered arcs with two heavier Ranger 2 dark orbs and a purple magic pulse.",
     [N([0, 1]), S("travel", "opal_ghost", "orb", (L, 0), 30, "OpalProjectile (looping arcs)", n=3), D("reaction", [9], (H, 0), 24, "OpalFx (orbit)", n=2, note="Ranger 2 e118 dark purple orbs with rim"), S("reaction", "opal_ghost", "wisp", (H, 4), 20, "OpalResidual", n=2), Q("cue", "OpalReactMagic purple", (H, 0))],
     "Confusion template (looping ghost orbs); reuses the B2 ghost sheet."),
  "alts": [V("Existing ghost", "opal_existing", "Ghost sheet only.", [N([0, 1]), S("travel", "opal_ghost", "orb", (L, 0), 30, "OpalProjectile", n=3), S("reaction", "opal_ghost", "wisp", (H, 4), 20, "OpalResidual", n=2)], "Zero new tiles."),
           V("Green wisp contrast", "native+donor", "Emerald blue-green orb as a contrast orb.", [N([0, 1]), D("travel", [8], (L, 0), 30, "OpalProjectile", n=3), Q("cue", "OpalReactMagic purple", (H, 0))], "Lighter, brighter orbs.")]},
 "Poison Powder": {"primary": V("Toxic pollen cloud", "native+opal", "Native defender emitter; purple flecks drift in with a PMD speck cloud and a purple tint on the target.",
     [N([0]), S("travel", WIND, "flecks", (L, 0), 40, "OpalProjectile (purple palette variant)", n=3, note="needs a purple palette variant of the wind sheet"), D("reaction", [4], (H, 0), 24, "OpalResidual", n=2, note="PMD effect.bin#266 purple/white specks"), Q("cue", "OpalReactMagic purple", (H, 0))],
     "Status-powder template (poison pollen)."),
  "alts": [V("Flecks only", "opal_existing", "Wind flecks in a purple palette.", [N([0]), S("travel", WIND, "flecks", (L, 0), 40, "OpalProjectile", n=3), Q("cue", "OpalReactMagic purple", (H, 0))], "Cheapest."),
           V("Toxic puffs", "native+opal", "Borrowed Toxic soft puff masks in purple.", [N([0]), NB("toxic", (L, 0), "soft puff masks"), Q("cue", "OpalReactMagic purple", (H, 0))], "Cloudier.")]},
 "Sleep Powder": {"primary": V("Drifting spores to drowse", "native+opal", "Native defender emitter; three soft pink clouds drift over, then lavender and blue 'z' glyphs rise, with a blue magic tint.",
     [N([0]), D("travel", [6], (L, 0), 30, "OpalProjectile (arc 6)", n=3, note="Emerald pink_cloud.png"), D("reaction", [2, 1], (H, 4), 36, "OpalResidual (z drift)", n=3, note="Emerald snore_z.png + z.png"), Q("cue", "OpalReactMagic blue", (H, 0))],
     "Status-powder template (sleep pollen)."),
  "alts": [V("Z only", "native+donor", "Native powder + z glyphs.", [N([0]), D("reaction", [1], (H, 4), 36, "OpalResidual", n=3), Q("cue", "OpalReactMagic blue", (H, 0))], "Cheapest."),
           V("Scent petals", "native+opal", "Borrowed Sweet Scent petal/haze masks.", [N([0]), NB("sweet_scent", (L, 0), "petal + haze masks"), D("reaction", [1], (H, 4), 36, "OpalResidual", n=3)], "Floral.")]},
 "Stun Spore": {"primary": V("Yellow pollen to static", "native+opal", "Native defender emitter; white/tan spore balls on arcs, installed thunder sparks and Ranger 2 lightning strands on the target.",
     [N([0]), D("travel", [7], (L, 0), 30, "OpalProjectile (arc 6)", n=3, note="Emerald spore.png"), S("reaction", "opal_thunder", "sparks", (H, 0), 12, "OpalImpactBurst", n=2), D("reaction", [5], (H, 2), 20, "OpalImpactBurst", n=2, note="Ranger 2 e103 yellow lightning strands"), Q("cue", "OpalReactMagic yellow", (H, 0))],
     "Status-powder template (stun pollen)."),
  "alts": [V("Sparks only", "opal_existing", "Thunder sparks only.", [N([0]), S("reaction", "opal_thunder", "sparks", (H, 0), 12, "OpalImpactBurst", n=2), Q("cue", "OpalReactMagic yellow", (H, 0))], "Zero new tiles."),
           V("Emerald zig-zag", "native+donor", "Emerald spark_1 zig-zag arcs.", [N([0]), D("reaction", [2], (H, 0), 14, "OpalImpactBurst", n=2), Q("cue", "OpalReactMagic yellow", (H, 0))], "Lighter static read.")]},
 "Swords Dance": {"primary": V("Orbiting blades (custom composite)", "custom_composite", "Native glow + sword-mask emitters; four blue blades orbit the user (baked orbit animation), a charge aura and a final white-blue flash.",
     [N([1, 0], "native sparkle + sword mask at the attacker"),
      X("Orbit", "DS OBJ sprites cannot rotate in the sheet pipeline: bake a 12-step orbit animation from TWO pixel-exact blade frames (upright, horizontal); the other orientations come from hflip/vflip. Four blades start 90 degrees apart and rotate once over ~36 frames."),
      D("launch", [7], (L, 4), 40, "OpalFx x4 (baked orbit animation)", n=4, note="Emerald sword.png (blue blade); 2 baked frames"), S("launch", RING, "ring_converge", (L, 0), 14, "OpalChargeAura", variant="steel"), S("aftermath", RING, "star_pop", (L, 36), 7, "OpalImpactBurst (targets=attacker)", variant="steel"), Q("cue", "OpalLightPulse white", (L, 38))],
     "Status-buff template (orbiting blades). Composite: no pool contains an orbit set; the blade art exists (Emerald), the orbit is authored."),
  "alts": [V("Single blade rise", "native+donor", "One blade rises and glints.", [N([1, 0]), D("launch", [7], (L, 4), 30, "OpalFx (rise)", n=1), Q("cue", "OpalLightPulse white", (L, 30))], "Much cheaper; no orbit."),
           V("Native + ring", "opal_existing", "Native emitters with a steel ring flourish.", [N([1, 0]), S("launch", RING, "ring_converge", (L, 0), 14, "OpalChargeAura", variant="steel"), S("aftermath", RING, "star_pop", (L, 30), 7, "OpalImpactBurst", variant="steel")], "Zero new tiles.")]},
 "Defense Curl": {"primary": V("Curl glint", "native+opal", "Native sphere + crescent emitters; a gold defensive ring pulse and a borrowed Disable star glint, with a white light pulse.",
     [N([0, 1]), S("launch", RING, "flat_expand", (L, 0), 12, "OpalChargeAura", variant="gold"), NB("disable", (L, 12), "four-point star glint masks (Platinum Disable)"), Q("cue", "OpalLightPulse white", (L, 12))],
     "Defensive-curl glint template."),
  "alts": [V("Ring only", "opal_existing", "Gold ring pulse.", [N([0, 1]), S("launch", RING, "flat_expand", (L, 0), 12, "OpalChargeAura", variant="gold")], "Zero new tiles."),
           V("Shell glint", "native+opal", "Borrowed Withdraw shell masks + an Emerald glint.", [N([0, 1]), NB("withdraw", (L, 0), "shell masks"), D("aftermath", [2], (L, 12), 14, "OpalImpactBurst (targets=attacker)", n=2)], "More shell-like.")]},
 "Focus Energy": {"primary": V("Tightening aura", "native+opal", "Native gradient/spire emitters; three red-orange rings converge on the user, then twin glints.",
     [N([1, 0]), S("launch", RING, "ring_converge", (L, 0), 30, "OpalChargeAura (3 rings)", n=3, variant="fire"), D("aftermath", [2], (L, 30), 14, "OpalImpactBurst (targets=attacker)", n=2, note="Emerald sparkle_3.png"), Q("cue", "OpalLightPulse orange", (L, 30))],
     "Focus-tightening template."),
  "alts": [V("Rings only", "opal_existing", "Fire-palette converging rings.", [N([1, 0]), S("launch", RING, "ring_converge", (L, 0), 30, "OpalChargeAura", n=3, variant="fire")], "Zero new tiles."),
           V("Glaring eyes", "native+donor", "Diamond red glaring eyes flash.", [N([1, 0]), D("launch", [9], (L, 10), 20, "OpalChargeAura"), S("launch", RING, "ring_converge", (L, 0), 20, "OpalChargeAura", variant="fire")], "Intense-focus read; large tile cost.")]},
 "Sand Attack": {"primary": V("Directed grains", "native+opal", "Native emitters; a spray of tan grains and clods flung at the target and a dust puff on arrival.",
     [N([2, 3, 0, 1]), D("travel", [6, 7], (L, 0), 18, "OpalProjectile (3 lanes)", n=3, note="Emerald smokescreen_impact.png + flying_dirt.png"), S("reaction", WIND, "puff", (H, 0), 10, "OpalImpactBurst", n=2)],
     "Directed-grains template."),
  "alts": [V("Dust only", "opal_existing", "Wind puff only.", [N([2, 3, 0, 1]), S("reaction", WIND, "puff", (H, 0), 10, "OpalImpactBurst", n=3)], "Zero new tiles."),
           V("Smoke borrow", "native+opal", "Borrowed Smoke Screen / Sandstorm masks.", [N([2, 3, 0, 1]), NB("sandstorm", (H, 0), "dust puff + grain dots + haze masks")], "Native-look dust.")]},
 "String Shot": {"primary": V("Thread arc to wrap", "native+opal", "Native emitters + native string sprites; two thread arcs of different weight and a white wrap ring converging on the target.",
     [N([0], "native emitter; native string sprites stay"), D("travel", [7, 6], (L, 0), 20, "OpalProjectile (arc 12)", n=2, note="Emerald string.png + string_2.png"), S("reaction", RING, "flat_converge", (H, 0), 12, "OpalImpactBurst", variant="opal")],
     "Status-bind template (thread arc)."),
  "alts": [V("Strings only", "native+donor", "Thread arcs only.", [N([0]), D("travel", [7, 6], (L, 0), 20, "OpalProjectile", n=2)], "Cheaper."),
           V("Arc borrow", "native+opal", "Borrowed Aurora Beam arc masks as thread loops.", [N([0]), NB("aurora_beam", (L, 0), "bright arc masks"), S("reaction", RING, "flat_converge", (H, 0), 12, "OpalImpactBurst", variant="opal")], "Smoother arc.")]},
 "Leech Seed": {"primary": V("Seed, vines, drain", "native+opal", "Native bullet-seed emitters; a green seed lobbed to the target, vine strands wrap it, and leaves flutter back to the user.",
     [N([0, 1, 2]), D("travel", [6], (L, 0), 24, "OpalProjectile (arc 10)", note="Emerald seed_2.png"), D("reaction", [1, 2], (H, 0), 24, "OpalImpactBurst (vine strands)", n=2, note="Emerald vine.png + vine_2.png"), S("aftermath", NATURE, "leaf_flutter", (H, 6), 24, "OpalResidual", n=3), Q("cue", "OpalReactMagic green", (H, 0))],
     "Seed-bind template (seed impact + vine strands)."),
  "alts": [V("Nature only", "opal_existing", "Vine lash + flutter.", [N([0, 1, 2]), S("reaction", NATURE, "vine_lash", (H, 0), 14, "OpalImpactBurst", n=2), S("aftermath", NATURE, "leaf_flutter", (H, 6), 24, "OpalResidual", n=3)], "Zero new tiles."),
           V("Whip borrow", "native+donor", "Borrowed Vine Whip crescents + seed.", [N([0, 1, 2]), D("travel", [6], (L, 0), 24, "OpalProjectile"), NB("vine_whip", (H, 0), "burst + crescent masks")], "Whip-like vines.")]},
 "Supersonic": {"primary": V("Resonant rings", "native+opal", "Native arc emitter; three expanding steel-blue rings and installed sound arcs sweep to the target.",
     [N([0]), S("travel", RING, "ring_expand", (L, 0), 30, "OpalProjectile (3 rings)", n=3, variant="steel"), S("travel", "opal_b9_sense", "sound_arc", (L, 4), 30, "OpalProjectile", n=3), Q("cue", "OpalReactMagic blue", (H, 0))],
     "Status-sound template (pulsing sound rings)."),
  "alts": [V("Arcs only", "opal_existing", "Sound arcs only.", [N([0]), S("travel", "opal_b9_sense", "sound_arc", (L, 0), 30, "OpalProjectile", n=3)], "Zero new tiles."),
           V("Cyan rings", "native+donor", "Ranger 2 cyan bubble rings.", [N([0]), D("travel", [9], (L, 0), 30, "OpalProjectile", n=3), Q("cue", "OpalReactMagic blue", (H, 0))], "Brighter rings.")]},
 "Double Team": {"primary": V("Echo afterimages (custom composite)", "custom_composite", "The native script already spawns real battler-sprite copies; keep it and add staggered tinted afterimages, speed dust at the feet, ground shadows and shimmer pulses.",
     [N([], "native script: 4 attacker sprite copies + 1 partner copy, Func_DoubleTeam sway, blink"),
      X("Afterimages", "The silhouettes are the battler itself (no art to find): tint each sprite copy with Func_FadeBattlerSprite at staggered white/cyan alpha. VERIFY at runtime that Func_FadeBattlerSprite accepts BATTLE_ANIM_MON_SPRITE_n copies (not proven by source reading)."),
      S("launch", WIND, "puff", (L, 0), 10, "OpalFx (feet dust)", n=5), D("launch", [7], (L, 0), 40, "OpalFx (ground ellipses under each copy)", n=5, note="Emerald white_shadow.png"), Q("cue", "OpalLightPulse white", (L, 0)), Q("cue", "OpalLightPulse white", (L, 36))],
     "Evasion template (echo silhouettes). Composite built on the battler copies the engine already draws."),
  "alts": [V("Dust and pulse", "opal_existing", "Wind dust + light pulses only.", [N([]), S("launch", WIND, "puff", (L, 0), 10, "OpalFx", n=5), Q("cue", "OpalLightPulse white", (L, 0))], "Zero new tiles."),
           V("Agility streaks", "native+opal", "Borrowed Agility soft streak masks as speed trails.", [N([]), NB("agility", (L, 0), "soft streak masks"), S("launch", WIND, "puff", (L, 0), 10, "OpalFx", n=5)], "Streakier.")]},
}
