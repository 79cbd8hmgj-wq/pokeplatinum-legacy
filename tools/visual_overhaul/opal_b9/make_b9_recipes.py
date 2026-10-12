#!/usr/bin/env python3
"""Writes the Opal B9 (everyday moves, P0) FX-sheet recipes into tools/visual_overhaul/opal_fx/recipes/.

The recipes are plain data for build_opal_fx_sheet.py (same pipeline as the B2 sheets). Every donor file named
here is a pokeemerald battle-anim PNG (FireRed's copies are byte-identical, see docs/visual_overhaul/opal_b9/CANDIDATE_MATRIX.md).
Frame rectangles come from the donor's own frame geometry (frame height = source sprite template height).

  python3 tools/visual_overhaul/opal_b9/make_b9_recipes.py
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "opal_fx/recipes"
SP = "graphics/battle_anims/sprites/"


def src(name, **kw):
    d = {"type": "emerald_png", "path": f"{SP}{name}.png"}
    d.update(kw)
    return d


def rows(sid, prefix, n, w, h, pick=None, **extra):
    """Frames cut from a vertical strip of n frames (w x h each)."""
    out = []
    for i in (pick if pick is not None else range(n)):
        f = {"id": f"{prefix}{i}", "src": sid, "rect": [0, i * h, w, h]}
        f.update(extra)
        out.append(f)
    return out


def seq(name, frames, loop=False):
    d = {"name": name, "frames": [[f, d] for f, d in frames]}
    if loop:
        d["loop"] = True
    return d


RECIPES = {}

# ---- strike: hit flashes, claw/fang/pierce contact art, ember + spark primitives (warm palette) ----
RECIPES["opal_b9_strike"] = {
    "name": "opal_b9_strike",
    "donor": "pokeemerald (FireRed/LeafGreen copies are byte-identical)",
    "sources": {
        "hit": src("hit"), "impact": src("impact"), "fury": src("fury_swipes"), "slash": src("slash"),
        "fangs": src("fangs"),
    },
    "frames": (
        rows("hit", "hit", 5, 32, 32, pick=[0, 1, 2, 4])
        + [{"id": "star", "src": "impact", "rect": [0, 0, 32, 32]}]
        + rows("fury", "furyA", 4, 32, 32, pick=[0, 1, 2])
        + rows("fury", "furyB", 4, 32, 32, pick=[0, 1, 2], hflip=True)
        + rows("slash", "streak", 4, 32, 32, pick=[1])
        + rows("fangs", "jaw", 2, 32, 32)
    ),
    "sequences": [
        seq("hit_small", [("hit0", 2), ("hit1", 2), ("hit2", 3), ("hit4", 3)]),          # 0
        seq("star_pierce", [("star", 5), ("star", 3)]),                                  # 1
        seq("claw_a", [("furyA0", 2), ("furyA1", 4), ("furyA2", 4)]),                    # 2
        seq("claw_b", [("furyB0", 2), ("furyB1", 4), ("furyB2", 4)]),                    # 3
        seq("jaw_upper", [("jaw0", 40)]),                                                # 4
        seq("jaw_lower", [("jaw1", 40)]),                                                # 5
        seq("streak", [("streak1", 12)]),                                                # 6
    ],
}

# ---- ember: small flame clusters + jumping spark arcs (Ember, ThunderShock) ----
RECIPES["opal_b9_ember"] = {
    "name": "opal_b9_ember",
    "donor": "pokeemerald (FireRed/LeafGreen copies are byte-identical)",
    "sources": {"ember": src("small_ember"), "spark": src("spark_h")},
    "frames": (
        rows("ember", "emb", 5, 32, 32, pick=[1, 2, 3])
        + [{"id": "spk0", "src": "spark", "rect": [0, 0, 32, 16]}, {"id": "spk1", "src": "spark", "rect": [0, 16, 32, 16]}]
    ),
    "sequences": [
        seq("ember", [("emb1", 3), ("emb2", 3), ("emb3", 3), ("emb2", 3)], loop=True),   # 0
        seq("spark_arc", [("spk0", 2), ("spk1", 2)], loop=True),                         # 1
        seq("ember_pop", [("emb1", 2), ("emb2", 3), ("emb3", 3)]),                       # 2
    ],
}

# ---- nature: leaves, razor leaf, vine lash (greens) ----
RECIPES["opal_b9_nature"] = {
    "name": "opal_b9_nature",
    "donor": "pokeemerald (FireRed/LeafGreen copies are byte-identical)",
    "sources": {"leaf": src("leaf"), "razor": src("razor_leaf"), "vine": src("vine_2")},
    "frames": (
        rows("leaf", "leaf", 9, 16, 16, pick=[0, 1, 3, 5, 8])
        + [{"id": "razor", "src": "razor", "rect": [0, 0, 32, 16]}]
        + rows("vine", "vine", 5, 32, 32)
    ),
    "sequences": [
        seq("leaf_spin", [("leaf0", 3), ("leaf1", 3), ("leaf3", 3), ("leaf5", 3), ("leaf8", 3)], loop=True),  # 0
        seq("razor_blade", [("razor", 40)]),                                                                  # 1
        seq("vine_lash", [("vine0", 2), ("vine1", 2), ("vine2", 3), ("vine3", 3), ("vine4", 4)]),             # 2
        seq("leaf_flutter", [("leaf8", 4), ("leaf5", 4), ("leaf3", 4), ("leaf1", 4)], loop=True),             # 3
    ],
}

# ---- wind: streaks, swirl, dust puffs, snow flecks (greys / blues; `ice` palette variant for Powder Snow) ----
RECIPES["opal_b9_wind"] = {
    "name": "opal_b9_wind",
    "donor": "pokeemerald (FireRed/LeafGreen copies are byte-identical)",
    "sources": {"wave": src("air_wave"), "wave2": src("air_wave_2"), "swirl": src("whirlwind"), "dust": src("speed_dust"),
                "snow": src("snowball")},
    "frames": (
        [{"id": "wave", "src": "wave", "rect": [0, 0, 32, 16]}, {"id": "wave_f", "src": "wave", "rect": [0, 0, 32, 16], "hflip": True},
         {"id": "crescent", "src": "wave2", "rect": [0, 0, 32, 16]},
         {"id": "swirl", "src": "swirl", "rect": [0, 0, 64, 64]}]
        + rows("dust", "dust", 3, 16, 16)
        + rows("snow", "snow", 6, 8, 8, pick=[0, 1, 2, 3])
    ),
    "sequences": [
        seq("streak", [("wave", 30)]),                                                    # 0
        seq("crescent", [("crescent", 30)]),                                              # 1
        seq("swirl", [("swirl", 40)]),                                                    # 2
        seq("puff", [("dust0", 3), ("dust1", 3), ("dust2", 4)]),                          # 3
        seq("flecks", [("snow0", 4), ("snow1", 4), ("snow2", 4), ("snow3", 4)], loop=True),  # 4
        seq("streak_f", [("wave_f", 30)]),                                                # 5
    ],
    "palette_variants": {"ice": {"ramp": ["#1a55b0", "#4aa6ee", "#b5ecff", "#ffffff"]}},
}

# ---- rock: boulder, fragments, dirt ----
RECIPES["opal_b9_rock"] = {
    "name": "opal_b9_rock",
    "donor": "pokeemerald (FireRed/LeafGreen copies are byte-identical)",
    "sources": {"rocks": src("rocks"), "flat": src("flat_rock"), "dirt": src("flying_dirt")},
    "frames": (
        rows("rocks", "rock", 6, 32, 32, pick=[0, 1, 3, 4, 5])
        + rows("flat", "shard", 5, 16, 16, pick=[0, 1, 2, 3, 4])
        + [{"id": "dirt0", "src": "dirt", "rect": [0, 0, 32, 16]}, {"id": "dirt1", "src": "dirt", "rect": [0, 16, 32, 16]}]
    ),
    "sequences": [
        seq("boulder", [("rock0", 4), ("rock1", 4)], loop=True),                                       # 0
        seq("break", [("rock1", 3), ("rock3", 3), ("rock4", 3), ("rock5", 4)]),                         # 1
        seq("shards", [("shard0", 3), ("shard1", 3), ("shard2", 3), ("shard3", 3), ("shard4", 3)], loop=True),  # 2
        seq("dirt", [("dirt0", 4), ("dirt1", 6)]),                                                      # 3
    ],
}

# ---- bubble: floating bubbles and pops ----
RECIPES["opal_b9_bubble"] = {
    "name": "opal_b9_bubble",
    "donor": "pokeemerald (FireRed/LeafGreen copies are byte-identical)",
    "sources": {"bubble": src("bubble"), "small": src("small_bubbles"), "pop": src("bubble_burst"), "pop2": src("bubble_burst_2")},
    "frames": (
        rows("bubble", "bub", 3, 16, 16, pick=[0, 1])
        + rows("small", "sm", 2, 16, 16)
        + rows("pop", "pop", 7, 16, 16, pick=[1, 2, 3, 4, 6])
        + rows("pop2", "big", 5, 32, 32, pick=[0, 1, 2, 3])
    ),
    "sequences": [
        seq("bubble", [("bub0", 8), ("bub1", 8)], loop=True),                                         # 0
        seq("bubble_small", [("sm0", 8), ("sm1", 8)], loop=True),                                     # 1
        seq("pop", [("pop1", 2), ("pop2", 2), ("pop3", 2), ("pop4", 3), ("pop6", 3)]),                # 2
        seq("pop_big", [("big0", 3), ("big1", 3), ("big2", 3), ("big3", 4)]),                         # 3
    ],
}

# ---- sense: eye glints, sound arcs, jagged roar lines (status moves) ----
RECIPES["opal_b9_sense"] = {
    "name": "opal_b9_sense",
    "donor": "pokeemerald (FireRed/LeafGreen copies are byte-identical)",
    "sources": {"leer": src("leer"), "waves": src("movement_waves"), "noise": src("noise_line")},
    "frames": (
        rows("leer", "gl", 5, 32, 32, pick=[0, 1, 2, 3])
        + rows("waves", "arc", 3, 32, 32)
        + rows("noise", "jag", 4, 32, 32, pick=[0, 2])
    ),
    "sequences": [
        seq("glint", [("gl0", 2), ("gl1", 3), ("gl2", 4), ("gl3", 3)]),                              # 0
        seq("sound_arc", [("arc0", 3), ("arc1", 3), ("arc2", 4)]),                                   # 1
        seq("roar_jag", [("jag0", 3), ("jag2", 3), ("jag0", 3)]),                                    # 2
    ],
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, r in RECIPES.items():
        (OUT / f"{name}.json").write_text(json.dumps(r, indent=1) + "\n")
        print("wrote", name)


if __name__ == "__main__":
    main()
