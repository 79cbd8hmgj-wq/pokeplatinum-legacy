#!/usr/bin/env python3
"""G7.6 overworld atmosphere generator (authority for every G7.6 asset).

Every output is derived from blobs pinned at BASE_REV (the pre-G7.6 tree), so
the generator is idempotent: rerunning it rewrites byte-identical outputs and
never compounds a grade.

Outputs
  * res/field/lighting/lighting_set_*.json   (in-place grades + new sets 015-019)
  * res/field/maps/texture_sets/*.nsbtx      (palette-only grades, via
                                              recolor_g76_atmosphere.c)
  * res/field/area_data/area_data_*.json     (re-pointed lighting sets)
  * res/field/lighting/lighting_sets.order, meson.build registration
  * docs/visual_overhaul/G7_6_ATMOSPHERE_REPORT.json

Texture grades never change dimensions, texel indices or resource names.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_REV = "896570704f269ebdf3bb96d4767319f782a1305a"
REPORT = ROOT / "docs/visual_overhaul/G7_6_ATMOSPHERE_REPORT.json"
TEX_DIR = "res/field/maps/texture_sets"
LIGHT_DIR = "res/field/lighting"
AREA_DIR = "res/field/area_data"

DAY = (9000, 30600)  # same daylight window the G4 passes used


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def git_blob(path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{BASE_REV}:{path}"], cwd=ROOT, check=True, capture_output=True
    ).stdout


def base_json(path: str):
    return json.loads(git_blob(path))


def write_json(path: str, data) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=4) + "\n")


def clamp(v: int) -> int:
    return max(0, min(31, v))


def scale_color(color: dict, mul, add=(0, 0, 0)) -> None:
    for ch, m, a in zip(("red", "green", "blue"), mul, add):
        color[ch] = clamp(int(color[ch] * m + a + 0.5))


FIELDS = {
    "light0": lambda k: k["lights"][0],
    "light2": lambda k: k["lights"][2],
    "diffuse": lambda k: k,
    "ambient": lambda k: k,
    "specular": lambda k: k,
    "emission": lambda k: k,
}
COLOR_KEY = {
    "light0": "color", "light2": "color", "diffuse": "diffuseColor",
    "ambient": "ambientColor", "specular": "specularColor", "emission": "emissionColor",
}


def grade_lighting(keyframes: list, spec: list) -> list:
    """spec: (scope, field, mul, add); scope 'all' or 'day'. Structure
    (endTime, enabled flags, directions) is never touched; disabled lights
    stay black."""
    for kf in keyframes:
        is_day = DAY[0] <= kf["endTime"] <= DAY[1]
        for scope, field, mul, add in spec:
            if scope == "day" and not is_day:
                continue
            holder = FIELDS[field](kf)
            if field in ("light0", "light2") and not holder["enabled"]:
                continue
            scale_color(holder[COLOR_KEY[field]], mul, add)
    return keyframes


# --------------------------------------------------------------------------
# lighting specs
# --------------------------------------------------------------------------
Z = (0, 0, 0)
LIGHTING_INPLACE = {
    # 1 Eterna: deeper canopy shade, cooler shadows, controlled green key.
    "lighting_set_010": ("lighting_set_010", [
        ("all", "light0", (0.95, 0.98, 1.04), Z),
        ("all", "diffuse", (0.94, 0.97, 1.00), Z),
        ("all", "ambient", (0.92, 0.97, 1.08), Z),
        ("all", "specular", (0.90, 0.95, 1.00), Z),
        ("all", "emission", (0.93, 0.97, 1.03), Z),
        ("day", "light0", (0.96, 0.98, 1.03), Z),
        ("day", "ambient", (1, 1, 1), (0, 0, 1)),
    ]),
    # 2 Snow region: colder ambient, less flat-white key.
    "lighting_set_011": ("lighting_set_011", [
        ("all", "light0", (0.95, 0.98, 1.05), Z),
        ("all", "diffuse", (0.94, 0.97, 1.04), Z),
        ("all", "ambient", (0.94, 0.98, 1.10), Z),
        ("all", "specular", (0.90, 0.93, 1.00), Z),
        ("all", "emission", (0.92, 0.95, 1.00), Z),
        ("day", "ambient", (1, 1, 1), (0, 0, 1)),
    ]),
    # 3 Galactic facility: darker structure, cyan-leaning highlights.
    "lighting_set_006": ("lighting_set_006", [
        ("all", "diffuse", (0.92, 0.96, 0.98), Z),
        ("all", "ambient", (0.85, 0.92, 1.00), Z),
        ("all", "specular", (0.95, 1.00, 1.04), Z),
        ("all", "emission", (0.90, 0.95, 1.00), Z),
    ]),
    # 4 Mt. Coronet lower floors (fog is applied in fieldmap.c).
    "lighting_set_007": ("lighting_set_007", [
        ("all", "light0", (0.92, 0.96, 1.06), Z),
        ("all", "diffuse", (0.92, 0.96, 1.04), Z),
        ("all", "ambient", (0.95, 0.98, 1.10), Z),
        ("all", "specular", (0.95, 0.98, 1.04), Z),
    ]),
    # 4 Spear Pillar: harder sun, deeper cool shade.
    "lighting_set_012": ("lighting_set_012", [
        ("day", "light0", (1.00, 1.00, 1.04), Z),
        ("day", "diffuse", (0.97, 0.98, 1.02), Z),
        ("day", "ambient", (0.88, 0.92, 1.08), Z),
        ("day", "specular", (0.95, 0.98, 1.04), Z),
        ("all", "ambient", (0.95, 0.97, 1.04), Z),
    ]),
    # 5 Distortion World: indigo/violet, deeper ambient, cyan-violet fill.
    "lighting_set_009": ("lighting_set_009", [
        ("all", "light0", (0.90, 0.85, 1.06), Z),
        ("all", "light2", (0.80, 0.85, 1.06), Z),
        ("all", "diffuse", (0.90, 0.88, 1.04), Z),
        ("all", "ambient", (0.85, 0.80, 1.05), Z),
        ("all", "specular", (0.85, 0.85, 1.04), Z),
        ("all", "emission", (0.80, 0.75, 1.00), Z),
    ]),
    # 6 Sinnoh lakes: cool atmospheric distance.
    "lighting_set_013": ("lighting_set_013", [
        ("day", "light0", (0.95, 1.00, 1.04), Z),
        ("day", "diffuse", (0.96, 1.00, 1.03), Z),
        ("day", "ambient", (0.92, 1.00, 1.08), Z),
        ("day", "specular", (0.95, 1.00, 1.04), Z),
    ]),
    # 7 Turnback Cave: darker, colder, violet-tinted fill.
    "lighting_set_014": ("lighting_set_014", [
        ("all", "light0", (0.85, 0.90, 1.00), Z),
        ("all", "light2", (1.40, 1.00, 1.20), Z),
        ("all", "diffuse", (0.85, 0.88, 0.98), Z),
        ("all", "ambient", (0.80, 0.85, 1.00), Z),
        ("all", "specular", (0.90, 0.90, 1.00), Z),
        ("all", "emission", (0.85, 0.85, 1.00), Z),
    ]),
}

# New dedicated sets: (new id, base set it is derived from, spec)
LIGHTING_NEW = {
    "lighting_set_015": ("lighting_set_001", [  # natural caves
        ("all", "light0", (0.88, 0.92, 1.04), Z),
        ("all", "light2", (0.90, 0.95, 1.05), Z),
        ("all", "diffuse", (0.88, 0.92, 1.00), Z),
        ("all", "ambient", (0.82, 0.88, 0.98), Z),
        ("all", "specular", (0.88, 0.92, 1.02), Z),
        ("all", "emission", (0.85, 0.90, 1.00), Z),
    ]),
    "lighting_set_016": ("lighting_set_007", [  # Mt. Coronet upper floors
        ("all", "light0", (0.92, 0.96, 1.06), Z),
        ("all", "diffuse", (0.92, 0.96, 1.04), Z),
        ("all", "ambient", (0.95, 0.98, 1.10), Z),
        ("all", "specular", (0.95, 0.98, 1.04), Z),
    ]),
    "lighting_set_017": ("lighting_set_000", [  # Sunyshore / Routes 223-224 coast
        ("day", "light0", (1.02, 1.00, 0.98), Z),
        ("day", "diffuse", (1.02, 1.02, 1.00), Z),
        ("day", "ambient", (0.95, 1.00, 1.05), Z),
        ("day", "specular", (1.05, 1.05, 1.05), Z),
    ]),
    "lighting_set_018": ("lighting_set_000", [  # Canalave / Route 218 / islands harbour
        ("day", "light0", (0.95, 0.99, 1.06), Z),
        ("day", "diffuse", (0.95, 0.98, 1.04), Z),
        ("day", "ambient", (0.92, 0.98, 1.10), Z),
        ("day", "specular", (0.95, 0.98, 1.05), Z),
    ]),
    "lighting_set_019": ("lighting_set_000", [  # Valor lakefront / Routes 213-214-222
        ("day", "light0", (0.97, 1.00, 1.04), Z),
        ("day", "diffuse", (0.97, 1.00, 1.02), Z),
        ("day", "ambient", (0.95, 1.02, 1.05), Z),
    ]),
}

AREA_LIGHT_REPOINT = {
    "area_data_013": "lighting_set_017",  # Sunyshore coast
    "area_data_015": "lighting_set_018",  # Canalave harbour / Route 218
    "area_data_018": "lighting_set_019",  # Valor lakefront / Routes 213, 214, 222
    "area_data_053": "lighting_set_015",  # Ravaged Path / Wayward Cave / Oreburgh Gate
    "area_data_055": "lighting_set_015",  # Oreburgh Mine
    "area_data_056": "lighting_set_015",  # Solaceon Ruins / Celestic Cave
    "area_data_057": "lighting_set_015",  # Stark Mountain / Rock Peak Ruins
    "area_data_071": "lighting_set_015",  # Victory Road
    "area_data_070": "lighting_set_016",  # Mt. Coronet 4F-6F
    "area_data_068": "lighting_set_006",  # Galactic lab / control room
    "area_data_077": "lighting_set_006",  # Galactic warehouse
}

# --------------------------------------------------------------------------
# texture rules  (see recolor_g76_atmosphere.c for the key meanings)
# --------------------------------------------------------------------------
def rule(names: str, **kw) -> str:
    return " ".join([f"names={names}"] + [f"{k}={v}" for k, v in kw.items()])


CANOPY = "tree01,conttree,conttree_b,conttree_t,conttree2_b,conttree2_t,tree2_01,plant2"
FOREST_GROUND = "grass,hage,lgreen,lgreenp,nectgrass,nhana,rhana,shana,tshadow,ckado,enccriff,fenter,newstep,puddlep,puddlep_x"
ROCK = "criff,criff2,criffp,apeak,hanger,searock,searock.1_pl,bridge,dun_bridge"
SHARED_SKIP = "kemuri,shadowchip,black,kage,fuchi"

CAVE_WALLS = ("dun_wall_c,dun_wall_c2,dun_wall_c2b,dun_wall_e,dun_wall_e2,dun_wall_e2b,dun_wall_n,dun_wall_n2,"
              "dun_wall_n2b,dun_wall_s,dun_wall_s2,dun_wall_s2b,dun_wall_w,dun_wall_w2,dun_wall_w2b,"
              "dun_wallsp1_01,dun_wallsp1_02,dun_wallsp1_03,dun_wallsp1_04,dun_wallsp1_05,dun_wallsp1_c,"
              "dun16_wall1,dun16_wall.5_pl,dun_apeak,apeak")
CAVE_FLOORS = ("dun_floor,dun_floor2,dun_floor3,dun_floor4,dun_step,dun_level,dun_slope,dun_yukasp1_01,"
               "dun_yukasp1_02,dun_yukasp1_03,dun_yukasp1_04,yuka_ora")
CAVE_DEPTH = "dun_hanger,dun_dhole,dun_dhole2,dun_dhole3,dun_dansou"

TEXTURE_JOBS: dict[str, dict] = {
    # ---- 1 Eterna Forest (dedicated set 074; G4A grade is the baseline) ----
    "map_texture_set_074": {"group": "1 Eterna", "rules": [
        rule(CANOPY, hmin=60, hmax=180, sat=0.90, con=1.14, lum=0.80, mulb=1.05, shb=0.06, shr=-0.02, shg=-0.01),
        rule(CANOPY, hmin=181, hmax=59, lum=0.90, shb=0.05, shr=-0.02),
        rule(FOREST_GROUND, hmin=60, hmax=150, sat=0.95, lum=0.92, shb=0.04, shr=-0.01),
        rule(ROCK, con=1.10, lum=0.92, shb=0.05, shr=-0.02),
    ]},
    # ---- 2 Snow region (dedicated area family 014: Snowpoint, Routes 216/217, Acuity, Coronet exterior) ----
    "map_texture_set_014": {"group": "2 Snow", "rules": [
        rule(f"*", skip=SHARED_SKIP + ",sea,puddle,puddle_b,lake,asasea,taki", lmax=0.45, con=1.12, lum=0.92, shb=0.03),
        rule(f"*", skip=SHARED_SKIP + ",sea,puddle,puddle_b,lake,asasea,taki", lmin=0.45, lmax=0.78, smax=0.45, shr=-0.03, shb=0.05, sat=1.08),
        rule(f"*", skip=SHARED_SKIP + ",sea,puddle,puddle_b,lake,asasea,taki", lmin=0.78, smax=0.35, lum=0.93, mulr=0.95, mulg=0.98, mulb=1.04),
        rule(f"*", skip=SHARED_SKIP, hmin=60, hmax=170, smin=0.2, sat=0.88, mulr=0.95, mulb=1.06),
    ]},
    # ---- 3 Galactic interiors ----
    "map_texture_set_057": {"group": "3 Galactic", "rules": [
        rule("*", skip=SHARED_SKIP + ",azt_win01,azt_win02,dun26_09,dun26_092,dun26_19", lmax=0.55, smax=0.30, con=1.15, lum=0.82, shb=0.04, shr=-0.02),
        rule("*", skip=SHARED_SKIP + ",azt_win01,azt_win02,dun26_09,dun26_092,dun26_19", lmin=0.55, smax=0.30, lum=0.92, mulr=0.94, mulb=1.06),
        rule("*", skip=SHARED_SKIP, hmin=170, hmax=230, smin=0.30, sat=1.15, lum=1.05),
        rule("*", skip=SHARED_SKIP + ",table_g01", hmin=10, hmax=60, smin=0.25, sat=0.80, lum=0.90),
    ]},
    "map_texture_set_067": {"group": "3 Galactic", "rules": [
        rule("*", skip=SHARED_SKIP, lmax=0.55, smax=0.30, con=1.15, lum=0.82, shb=0.04, shr=-0.02),
        rule("*", skip=SHARED_SKIP, lmin=0.55, smax=0.30, lum=0.92, mulr=0.94, mulb=1.06),
        rule("*", skip=SHARED_SKIP, hmin=170, hmax=230, smin=0.30, sat=1.15, lum=1.05),
        rule("*", skip=SHARED_SKIP, hmin=10, hmax=60, smin=0.25, sat=0.80, lum=0.90),
    ]},
    "map_texture_set_076": {"group": "3 Galactic", "rules": [
        rule("*", skip=SHARED_SKIP, con=1.10, lum=0.88, sat=0.82, mulr=0.95, mulb=1.05, shb=0.03),
    ]},
    # ---- 4 Mt. Coronet / Spear Pillar ----
    "map_texture_set_068": {"group": "4 Coronet", "rules": [
        rule(CAVE_WALLS, con=1.12, lum=0.86, shb=0.04, shr=-0.02),
        rule(CAVE_FLOORS, lum=1.03, sat=0.95, hir=0.01),
        rule(CAVE_DEPTH, con=1.10, lum=0.92, shb=0.03),
    ]},
    "map_texture_set_069": {"group": "4 Coronet", "rules": [
        rule(CAVE_WALLS, con=1.12, lum=0.86, sat=0.80, mulr=0.93, mulb=1.10, shb=0.04),
        rule(CAVE_FLOORS, lum=1.00, mulr=0.96, mulb=1.06, hir=0.01),
        rule(CAVE_DEPTH, con=1.10, lum=0.90, mulr=0.95, mulb=1.06),
    ]},
    "map_texture_set_059": {"group": "4 Spear", "rules": [
        rule("colum_a_pl,colum_b_pl,colum_c_pl,dun08_chip_a_pl,dun08_chip_b_pl,dun08_chip_c_pl,dun08_chip_d_pl,"
             "dun08_chip_e_pl,dun08_chip_f_pl,dun08_chip_g_pl,dun08_shin_b_pl,dun08_shin_d_pl,apeak,criff,criff2,criff3,hanger,searock",
             con=1.18, lum=0.90, mulr=0.94, mulb=1.07, shb=0.05),
    ]},
    # ---- 5 Distortion World ----
    "map_texture_set_073": {"group": "5 Distortion", "rules": [
        rule("s_land,s_land2,s_land_att,s_land3,s_land4,s_landp,s_land_jump_pl,s_grass", lmax=0.50, con=1.15, lum=0.85, shr=0.02, shb=0.05),
        rule("s_land,s_land2,s_land_att,s_land3,s_land4,s_landp,s_land_jump_pl,s_grass", lmin=0.50, sat=1.05, lum=1.04, hib=0.02),
        rule("criff,criffP2,tree_sbt01", con=1.12, lum=0.78, shr=0.01, shb=0.05),
    ]},
    # ---- 6 Lakes / coast (each family keeps its own water identity) ----
    "map_texture_set_061": {"group": "6 Lakes", "rules": [  # Verity / Valor / Sendoff: deep clear freshwater
        rule("sea,asasea", con=1.12, lum=0.88, mulr=0.84, mulg=1.00, mulb=1.05),
        rule("lake,puddle,puddle_x", mulr=0.94, mulg=0.98),
        rule("hamabe,asahamabe,taki", hmin=175, hmax=260, mulr=0.92, lum=0.95),
        rule("sandset,nsandp,beach,beachp", hir=0.02, lum=1.0),
    ]},
    "map_texture_set_013": {"group": "6 Coast Sunyshore", "rules": [  # bright turquoise resort sea
        rule("sea,asasea", sat=1.20, lum=1.06, mulr=0.86, mulg=1.06),
        rule("lake,puddle", mulr=0.94, mulg=1.02),
        rule("hamabe,asahamabe,taki", hmin=175, hmax=260, mulr=0.92, mulg=1.03),
        rule("sandset,nsandp,beach,beachp", hir=0.02, hig=0.01),
    ]},
    "map_texture_set_015": {"group": "6 Coast Canalave", "rules": [  # cold steel-blue harbour sea
        rule("sea,asasea", sat=0.95, con=1.08, lum=0.88, mulr=0.90, mulg=0.96, mulb=1.05),
        rule("lake,puddle", mulr=0.92, mulg=0.96),
        rule("hamabe,asahamabe,taki", hmin=175, hmax=260, mulr=0.90, lum=0.94),
        rule(ROCK + ",criff3,criff5", shb=0.04, shr=-0.02, con=1.06),
    ]},
    "map_texture_set_018": {"group": "6 Coast Valor lakefront", "rules": [  # teal-green lakeside
        rule("sea,asasea", lum=0.95, mulr=0.92, mulg=1.02),
        rule("lake,puddle", mulr=0.95),
        rule("hamabe,asahamabe,taki", hmin=175, hmax=260, mulr=0.93),
        rule("sandset,nsandp,beach,beachp", hir=0.015),
    ]},
    # ---- 7 Caves / Turnback ----
    "map_texture_set_052": {"group": "7 Caves", "rules": [
        rule(CAVE_WALLS, con=1.10, lum=0.88, mulr=0.94, mulg=0.98, mulb=1.06, shb=0.03),
        rule(CAVE_FLOORS, lum=1.02, sat=0.94, hir=0.01),
        rule(CAVE_DEPTH, con=1.10, lum=0.92, shb=0.03),
    ]},
    "map_texture_set_054": {"group": "7 Caves", "rules": [
        rule(CAVE_WALLS, con=1.10, lum=0.88, mulr=0.94, mulg=0.98, mulb=1.06, shb=0.03),
        rule(CAVE_FLOORS, lum=1.02, sat=0.94, hir=0.01),
        rule(CAVE_DEPTH, con=1.10, lum=0.92, shb=0.03),
    ]},
    "map_texture_set_055": {"group": "7 Caves", "rules": [
        rule(CAVE_WALLS, con=1.10, lum=0.88, mulr=0.94, mulg=0.98, mulb=1.06, shb=0.03),
        rule(CAVE_FLOORS, lum=1.02, sat=0.94, hir=0.01),
        rule(CAVE_DEPTH, con=1.10, lum=0.92, shb=0.03),
    ]},
    "map_texture_set_056": {"group": "7 Caves", "rules": [
        rule(CAVE_WALLS, con=1.10, lum=0.88, mulr=0.94, mulg=0.98, mulb=1.06, shb=0.03),
        rule(CAVE_FLOORS, lum=1.02, sat=0.94, hir=0.01),
        rule(CAVE_DEPTH, con=1.10, lum=0.92, shb=0.03),
    ]},
    "map_texture_set_070": {"group": "7 Caves", "rules": [
        rule(CAVE_WALLS, con=1.10, lum=0.88, mulr=0.94, mulg=0.98, mulb=1.06, shb=0.03),
        rule(CAVE_FLOORS, lum=1.02, sat=0.94, hir=0.01),
        rule(CAVE_DEPTH, con=1.10, lum=0.92, shb=0.03),
    ]},
    # Turnback: oppressive/unnatural. Saturated greens (suspected key colours,
    # see G4F) are excluded by the hue masks (green band 80-160 untouched).
    "map_texture_set_075": {"group": "7 Turnback", "rules": [
        rule(CAVE_WALLS, hmin=161, hmax=79, con=1.14, lum=0.82, mulr=0.98, mulg=0.92, mulb=1.08, shb=0.05, shr=0.01),
        rule(CAVE_FLOORS, hmin=161, hmax=79, lum=0.95, sat=0.90, mulr=1.04, mulg=0.94, mulb=1.06, shb=0.03),
        rule(CAVE_DEPTH, hmin=161, hmax=79, con=1.12, lum=0.85, mulr=0.98, mulg=0.92, mulb=1.08, shb=0.04),
    ]},
}


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def build_tool(workdir: Path) -> Path:
    nb = ROOT / "tools/nitrobtx"
    sources = [
        "src/common.c", "src/ns/chunks/tex.c", "src/ns/container.c", "src/ns/resource_dict.c",
        "src/ns/resource_name.c", "src/ns/resource_tree.c", "src/palette.c", "src/texture.c",
    ]
    exe = workdir / "recolor-g76"
    subprocess.run(
        ["gcc", "-std=gnu17", "-O2", f"-I{nb / 'include'}", *(str(nb / s) for s in sources),
         str(ROOT / "tools/visual_overhaul/recolor_g76_atmosphere.c"), "-lpng", "-lm", "-o", str(exe)],
        check=True,
    )
    return exe


def register_lighting_sets() -> None:
    order_path = ROOT / LIGHT_DIR / "lighting_sets.order"
    lines = [x for x in order_path.read_text().splitlines() if x]
    for name in LIGHTING_NEW:
        if name not in lines:
            lines.append(name)
    order_path.write_text("\n".join(lines) + "\n")

    meson = ROOT / LIGHT_DIR / "meson.build"
    text = meson.read_text()
    anchor = "    'lighting_set_014.json'),"
    if "'lighting_set_015.json'" not in text:
        extra = "".join(f"    '{n}.json',\n" for n in LIGHTING_NEW)
        text = text.replace(anchor, "    'lighting_set_014.json',\n" + extra.rstrip(",\n") + "),")
        meson.write_text(text)


def main() -> int:
    report: dict = {"base_rev": BASE_REV, "lighting": {}, "area_data": {}, "textures": {}}

    for name, (src, spec) in LIGHTING_INPLACE.items():
        write_json(f"{LIGHT_DIR}/{name}.json", grade_lighting(base_json(f"{LIGHT_DIR}/{src}.json"), spec))
        report["lighting"][name] = {"derived_from": src, "in_place": True}
    for name, (src, spec) in LIGHTING_NEW.items():
        write_json(f"{LIGHT_DIR}/{name}.json", grade_lighting(base_json(f"{LIGHT_DIR}/{src}.json"), spec))
        report["lighting"][name] = {"derived_from": src, "in_place": False}
    register_lighting_sets()

    for area, lighting in AREA_LIGHT_REPOINT.items():
        data = base_json(f"{AREA_DIR}/{area}.json")
        data["lightingSet"] = lighting
        write_json(f"{AREA_DIR}/{area}.json", data)
        report["area_data"][area] = lighting

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        exe = build_tool(tmpdir)
        for tex, job in TEXTURE_JOBS.items():
            rules_path = tmpdir / f"{tex}.rules"
            rules_path.write_text("\n".join(job["rules"]) + "\n")
            src = tmpdir / f"{tex}.base.nsbtx"
            src.write_bytes(git_blob(f"{TEX_DIR}/{tex}.nsbtx"))
            dst = ROOT / TEX_DIR / f"{tex}.nsbtx"
            result = subprocess.run([str(exe), str(rules_path), str(src), str(dst)],
                                    check=True, capture_output=True, text=True)
            changed = {}
            total = ""
            for line in result.stdout.splitlines():
                if line.startswith("TOTAL"):
                    total = line
                else:
                    pal, count = line.rsplit(": ", 1)
                    changed[pal] = int(count)
            if not changed:
                raise SystemExit(f"{tex}: grade matched no palettes")
            report["textures"][tex] = {"group": job["group"], "summary": total, "palettes": changed}

    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"G7.6: {len(LIGHTING_INPLACE)} lighting sets graded in place, {len(LIGHTING_NEW)} new, "
          f"{len(AREA_LIGHT_REPOINT)} area records re-pointed, {len(TEXTURE_JOBS)} texture sets graded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
