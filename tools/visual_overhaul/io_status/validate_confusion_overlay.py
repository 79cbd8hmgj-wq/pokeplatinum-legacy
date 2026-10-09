#!/usr/bin/env python3
"""Static checks for the IO-STATUS confusion overlay pilot.

Fails closed: every check asserts on the actual source text, so a refactor that
breaks an invariant must update this script deliberately.

Covers: status/mode gating, read-only battle access, render-state handling,
lifecycle safety, build registration, call-site placement and geometry/budget
bounds (orbit math is re-evaluated with the same fixed-point formulas).
Not a runtime or visual test.
"""
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OVERLAY_C = (ROOT / "src/battle/battle_status_overlay.c").read_text()
OVERLAY_H = (ROOT / "include/battle/battle_status_overlay.h").read_text()
BATTLE_MAIN = (ROOT / "src/battle/battle_main.c").read_text()
MESON = (ROOT / "src/meson.build").read_text()
LSF = (ROOT / "platinum.us/main.lsf").read_text()

failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)


def code_only(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


CODE = code_only(OVERLAY_C)


def function_body(name):
    m = re.search(r"^(?:static )?\w[\w \*]*\b" + name + r"\([^)]*\)\n\{(.*?)^\}", CODE, re.S | re.M)
    check(m is not None, f"function not found: {name}")
    return m.group(1) if m else ""


def define(name):
    m = re.search(r"^#define\s+" + name + r"\s+(.+)$", CODE, re.M)
    check(m is not None, f"missing #define {name}")
    return m.group(1).strip() if m else "0"


consts = {"FX32_ONE": 0x1000, "FX32_SHIFT": 12}


def const(name):
    expr = define(name)
    for k, v in sorted(consts.items(), key=lambda kv: -len(kv[0])):
        expr = expr.replace(k, str(v))
    for dep in re.findall(r"[A-Z][A-Z0-9_]+", expr):
        expr = expr.replace(dep, str(const(dep)))
    val = eval(expr.replace("/", "//"), {"__builtins__": {}})
    consts[name] = val
    return val


# ---------------------------------------------------------------- gating
can = function_body("CanDrawOverlay")
check("BattleSystem_GetRenderMode(battleSys) != 0" in can, "render mode 0 gate missing")
check("BattleSystem_IsInitialized(battleSys)" in can, "battle-initialized gate missing")
for t in ("BATTLE_TYPE_LINK", "BATTLE_TYPE_SAFARI", "BATTLE_TYPE_PAL_PARK", "BATTLE_TYPE_CATCH_TUTORIAL"):
    check(t in can, f"battle-type exclusion missing: {t}")
check("BATTLE_STATUS_RECORDING" in can, "recording/playback exclusion missing")

draw = function_body("BattleStatusOverlay_Draw")
check("if (!CanDrawOverlay(battleSys))" in draw, "Draw must early-out on CanDrawOverlay")
check("if (battleCtx == NULL)" in draw, "Draw must NULL-check the battle context")
check("if (count == 0)" in draw and draw.index("if (count == 0)") < draw.index("G3_PushMtx"),
      "must return before any G3 command when no battler qualifies")

anchor = function_body("TryGetAnchor")
check("BATTLEMON_VOLATILE_STATUS" in anchor and "VOLATILE_CONDITION_CONFUSION" in anchor,
      "confusion volatile read missing")
check("BATTLEMON_CUR_HP" in anchor, "HP==0 hide missing")
for attr in ("MON_SPRITE_HIDE", "MON_SPRITE_HIDE_2", "MON_SPRITE_PARTIAL_DRAW", "MON_SPRITE_ALPHA",
             "MON_SPRITE_SCALE_X", "MON_SPRITE_SCALE_Y", "MON_SPRITE_SHADOW_HEIGHT"):
    check(attr in anchor, f"visibility/position attribute not consulted: {attr}")
check(anchor.index("PokemonSprite_IsActive") < anchor.index("PokemonSprite_GetAttribute"),
      "IsActive must precede any attribute read")
check("monSprite == NULL" in anchor, "NULL check before IsActive missing")

# ------------------------------------------------- read-only / no resources
forbidden = [
    r"\bBattleMon_Set\b", r"\bBattleMon_Add", r"\bBattleContext_Set\b", r"\bstatusVolatile\s*(?:=|\|=|&=)",
    r"\bHeap_Alloc", r"\bHeap_Free", r"\bSysTask_Start\b", r"\bSysTask_Done\b",
    r"\bSpriteSystem_", r"\bManagedSprite", r"\bPaletteData_", r"\bG3_TexPlttBase\b",
    r"\bNNS_G2dLoadImage", r"\bPokemonSprite_SetAttribute\b", r"\bG3_MaterialColor",
    r"\bG3_SwapBuffers\b", r"\bG3_RequestSwapBuffers\b", r"\bOS_Alloc\b", r"\bGX_Load",
]
for pat in forbidden:
    check(re.search(pat, CODE) is None, f"forbidden construct present: {pat}")
check(re.search(r"^static\s+[^(\n]*(?:\*|=)[^(\n]*;", CODE, re.M) is None,
      "file-scope mutable/pointer state is not allowed")
check(re.search(r"^static\s+(?!BOOL|void)[^(\n]*;", CODE, re.M) is None, "unexpected file-scope variable")
check("BattleSystem_GetBattleContext(battleSys)" in draw, "battle context must be fetched per call")

# ------------------------------------------------------ render-state handling
check(draw.count("G3_PushMtx();") == 1 and draw.count("G3_PopMtx(1);") == 1, "Draw matrix push/pop unbalanced")
star = function_body("DrawStarPass")
check(star.count("G3_PushMtx();") == 1 and star.count("G3_PopMtx(1);") == 1, "star pass push/pop unbalanced")
check(star.count("G3_Begin(") == 1 and star.count("G3_End();") == 1, "Begin/End unbalanced")
check("NNS_G3dGeFlushBuffer();" in draw and draw.index("NNS_G3dGeFlushBuffer") < draw.index("G3_PushMtx"),
      "geometry flush must precede overlay commands")
none_idx = draw.index("G3_TexImageParam(GX_TEXFMT_NONE")
restore_idx = draw.index("G3_TexImageParam(monSpriteMan->imageProxy.attr.fmt")
check(none_idx < draw.index("DrawConfusionStars") < restore_idx < draw.rindex("G3_PopMtx(1);"),
      "texture param must be disabled before and restored after the overlay, inside the matrix pair")
check("monSpriteMan->charBaseAddr" in draw[restore_idx:], "restored TexImageParam must use charBaseAddr")
check("GX_LIGHTMASK_NONE" in draw and "GX_POLYGONMODE_MODULATE" in draw, "lighting must stay masked off")
check("31, 0);" in draw, "overlay polygons must be fully opaque")

# --------------------------------------------------------- call-site placement
m = re.search(r"^static void SysTask_DrawSprites\([^;]*?\)\n\{.*?^\}", BATTLE_MAIN, re.S | re.M)
check(m is not None, "SysTask_DrawSprites not found")
if m:
    body = m.group(0)
    seq = [body.find(s) for s in ("PokemonSpriteManager_DrawSprites(", "BattleStatusOverlay_Draw(",
                                  "SpriteSystem_DrawSprites(", "G3_RequestSwapBuffers(")]
    check(all(i >= 0 for i in seq) and seq == sorted(seq), "overlay must sit between mon draw and OAM draw/swap")
    check("renderMode == 0 || battleSys->renderMode == 3" in body, "overlay call must stay inside the mode 0/3 block")
check(BATTLE_MAIN.count("BattleStatusOverlay_Draw(") == 1, "overlay must have exactly one call site")
check('#include "battle/battle_status_overlay.h"' in BATTLE_MAIN, "battle_main.c include missing")
check("'battle/battle_status_overlay.c'" in MESON, "meson.build registration missing")
# The linker spec places objects per overlay explicitly; an unlisted object links "successfully" but
# stays unplaced (symbol at address 0), so the call would jump to 0 at runtime.
m = re.search(r"^Overlay battle\n\{(.*?)^\}", LSF, re.S | re.M)
check(m is not None and "Object main.nef.p/src_battle_battle_status_overlay.c.o" in m.group(1),
      "main.lsf: overlay object must be listed in the battle overlay (same overlay as its only caller)")
check("Object main.nef.p/src_battle_battle_main.c.o" in (m.group(1) if m else ""), "caller not in the battle overlay")
check("void BattleStatusOverlay_Draw(BattleSystem *battleSys);" in OVERLAY_H, "header prototype missing")

# ------------------------------------------------------------- geometry bounds
n_stars = const("ORBIT_STAR_COUNT")
step = const("ORBIT_STEP_PER_FRAME")
spacing = const("ORBIT_STAR_SPACING")
rx, ry = const("ORBIT_RADIUS_X"), const("ORBIT_RADIUS_Y")
hmin, hrange, grow = const("STAR_HALF_SIZE_MIN"), const("STAR_HALF_SIZE_RANGE"), const("STAR_OUTLINE_GROW")
arm, width = const("STAR_ARM_LENGTH"), const("STAR_ARM_WIDTH")
outline_z = const("STAR_OUTLINE_Z")
bias = const("STAR_DEPTH_FRONT_BIAS")
min_y = const("SCREEN_MIN_Y")
ppm = const("POLYGONS_PER_MON")
vpm = const("VERTICES_PER_MON")

check(n_stars == 3, "pilot expects 3 orbiting stars")
check(0 < step < 0x10000 and 0x10000 % step == 0, "orbit step must divide one revolution evenly")
check(spacing * n_stars <= 0x10000 and 0x10000 - spacing * n_stars < n_stars, "stars must be evenly spaced")
check(-0x8000 <= outline_z < 0 and arm <= 0x7FFF and 0 < width < arm, "vertex values must fit fx16 and be sane")
check(-outline_z > 0x400, "outline must sit clearly behind the fill (depth buffer resolution)")
check(ppm == 12 and vpm == 48, f"per-battler budget changed: {ppm} polygons / {vpm} vertices")
check(4 * ppm <= 64 and 4 * vpm <= 256, "four-battler budget exceeds pilot cap (64 polys / 256 vertices)")
check(len(re.findall(r"G3_Vtx\(", star)) == 8, "star pass must emit exactly two quads (8 vertices)")
check(hmin > 0 and bias > 0 and min_y > hmin + hrange + grow, "size / depth / clamp constants inconsistent")


def sin_idx(i):
    return int(round(math.sin(i / 65536.0 * 2 * math.pi) * 4096))


def cos_idx(i):
    return int(round(math.cos(i / 65536.0 * 2 * math.pi) * 4096))


half_seen = set()
min_dx = 10 ** 9
for frame in range(0x10000 // step):
    phase = (frame * step) & 0xFFFF
    for k in range(n_stars):
        a = (phase + k * spacing) & 0xFFFF
        s, c = sin_idx(a), cos_idx(a)
        dx, dy = (rx * c) >> 12, (ry * s) >> 12
        half = hmin + (((s + 0x1000) * hrange) >> 13)
        half_seen.add(half)
        check(hmin <= half <= hmin + hrange, f"half size out of range at frame {frame}: {half}")
        check(abs(dx) + half + grow <= rx + hmin + hrange + grow, "star leaves orbit envelope")
        check(abs(dy) <= ry, "star leaves vertical envelope")
        check(bias + (s >> 8) + outline_z // 0x1000 > 0, "fill and outline must stay in front of the battler quad (strictly nearer: depth test is LESS)")
        min_dx = min(min_dx, dx)
check(min(half_seen) == hmin and max(half_seen) == hmin + hrange, "size pulse does not span the configured range")

# horizontal screen safety for the narrowest sprite anchor: envelope must fit in 256px for x in [rx+max, 255-...]
envelope = rx + hmin + hrange + grow
check(2 * envelope < 256, "orbit envelope wider than the screen")

if failures:
    print("IO-STATUS confusion overlay validation FAILED:")
    for f in failures:
        print(" -", f)
    sys.exit(1)

print(f"IO-STATUS confusion overlay validation passed: {ppm} polygons / {vpm} vertices per battler "
      f"({4 * ppm} / {4 * vpm} worst case), half sizes {sorted(half_seen)}, {0x10000 // step}-frame orbit.")
