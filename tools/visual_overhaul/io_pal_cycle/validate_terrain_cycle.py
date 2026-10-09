#!/usr/bin/env python3
"""Static validation for IO-PAL-CYCLE (S2-D/S2-E): data-driven battle terrain palette animation.

Usage:
    validate_terrain_cycle.py                 # checks + mutation self-test
    validate_terrain_cycle.py --no-mutations  # checks only

Checks (S2-E)
  1. Config validity: unique terrains, palette bounds (firstIdx+count <= 16), count/phase caps,
     phase 0 == authored palette, step contrast limits, minimum interval (photosensitivity).
  2. Palette safety, per terrain and per day/evening/night variant: protected entries (index 0,
     black outline entries, each sprite's dominant body index) are never animated; animated entries
     cover a restrained share of drawn pixels in BOTH sprites; ramps are monotone; every phase is
     evaluated with the same BGR555 math as src/battle/terrain.c and bounded step-to-step and
     peak-to-base.
  3. Source contract: single task creation, ownership/index guards, render-mode + fade guards,
     faded==unfaded ownership check before any write, writes confined to the configured range,
     OBJ + BG slot 7 mirror, no allocation, cleanup on Terrain_Destroy and the battle exit path.
  4. Regression: only the four configured terrains animate; the water entry equals the merged pilot;
     terrain art/palettes are unchanged against the pinned baseline commit (when git has it).

Mutation self-test: deliberate defects applied to in-memory copies must each be rejected.
This is not a runtime or visual test (emulator QA was skipped by owner decision).
"""
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
BASELINE = "98b550a1fe7b6da6d317d753f6fa4cf10bb94dec"  # main before S2-D
TERRAIN_RES = "res/graphics/battle/terrain"

# Terrain -> (resource dir, palette files). 'all' terrains reuse one palette for every time of day.
TERRAINS = {
    "TERRAIN_WATER": ("water", ["day", "evening", "night"]),
    "TERRAIN_ICE": ("ice", ["day", "evening", "night"]),
    "TERRAIN_DISTORTION_WORLD": ("distortion_world", ["all"]),
    "TERRAIN_CAVE": ("cave", ["all"]),
}

MIN_INTERVAL = 8            # frames; >= 8 keeps any cycle well below 3 flashes/s per step
MAX_COVERAGE = 0.30         # animated entries may cover at most 30% of drawn pixels
MAX_STEP_LUM = 0.12         # per-step luminance change (0..1)
MAX_PEAK_LUM = 0.12         # distance from the authored palette (0..1)
MAX_GLOW_UNITS = 4          # 5-bit units
GLOW_STEP_UNITS = 1

CFG_RE = re.compile(
    r"\{\s*(TERRAIN_\w+),\s*(TERRAIN_CYCLE_\w+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*\{([^}]*)\}\s*\}"
)


class Fail(Exception):
    pass


def read(rel):
    return (ROOT / rel).read_text()


# ---------------------------------------------------------------- data model
def parse_configs(c_src):
    table = re.search(r"sTerrainCycleConfigs\[\]\s*=\s*\{(.*?)\n\};", c_src, re.S)
    if not table:
        raise Fail("sTerrainCycleConfigs table not found")
    body = re.sub(r"//[^\n]*", "", table.group(1))
    cfgs = []
    for m in CFG_RE.finditer(body):
        steps = [int(x) for x in m.group(7).replace(" ", "").split(",") if x != ""]
        cfgs.append(dict(terrain=m.group(1), mode=m.group(2), first=int(m.group(3)), count=int(m.group(4)),
                         interval=int(m.group(5)), phases=int(m.group(6)), steps=steps))
    if body.count("TERRAIN_CYCLE_") != len(cfgs) or not cfgs:
        raise Fail("config table contains entries the validator could not parse")
    return cfgs


def parse_limits(c_src, h_src):
    max_phases = int(re.search(r"#define TERRAIN_CYCLE_MAX_PHASES\s+(\d+)", c_src).group(1))
    max_colors = int(re.search(r"#define TERRAIN_CYCLE_MAX_COLORS\s+(\d+)", h_src).group(1))
    return max_phases, max_colors


def load_pal(path):
    lines = path.read_text().split()
    if lines[:3] != ["JASC-PAL", "0100", "16"]:
        raise Fail(f"{path}: not a 16-colour JASC palette")
    vals = [int(v) for v in lines[3:]]
    if len(vals) != 48:
        raise Fail(f"{path}: expected 48 components")
    return [tuple(vals[i:i + 3]) for i in range(0, 48, 3)]


def to555(rgb):
    return tuple(c >> 3 for c in rgb)  # same quantisation the NCLR converter applies


def lum(c5):
    r, g, b = c5
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 31.0


def sprite_counts(terrain_dir):
    out = {}
    for side in ("player", "enemy"):
        im = Image.open(ROOT / TERRAIN_RES / terrain_dir / f"{side}.png")
        if im.mode != "P":
            raise Fail(f"{terrain_dir}/{side}.png is not indexed")
        data = im.tobytes()
        counts = [0] * 16
        for v in data:
            if v > 15:
                raise Fail(f"{terrain_dir}/{side}.png uses palette index {v} > 15")
            counts[v] += 1
        out[side] = counts
    return out


# ---------------------------------------------------------------- C-equivalent phase model
def glow(c5, delta):
    return tuple(min(31, max(0, ch + delta)) for ch in c5)


def phase_colors(cfg, base, step):
    out = []
    for i in range(cfg["count"]):
        if cfg["mode"] == "TERRAIN_CYCLE_GLOW":
            out.append(glow(base[i], cfg["steps"][step]))
        else:
            src = min(max(i + cfg["steps"][step], 0), cfg["count"] - 1)
            out.append(base[src])
    return out


# ---------------------------------------------------------------- check groups
def check_configs(cfgs, max_phases, max_colors):
    seen = set()
    for c in cfgs:
        t = c["terrain"]
        if t in seen:
            raise Fail(f"{t}: duplicate config")
        seen.add(t)
        if t not in TERRAINS:
            raise Fail(f"{t}: configured but not covered by this validator")
        if c["mode"] not in ("TERRAIN_CYCLE_RAMP", "TERRAIN_CYCLE_GLOW"):
            raise Fail(f"{t}: unknown mode {c['mode']}")
        if not (1 <= c["count"] <= max_colors):
            raise Fail(f"{t}: count {c['count']} outside 1..{max_colors}")
        if c["first"] < 1 or c["first"] + c["count"] > 16:
            raise Fail(f"{t}: range {c['first']}+{c['count']} outside palette entries 1..15")
        if not (2 <= c["phases"] <= max_phases):
            raise Fail(f"{t}: phases {c['phases']} outside 2..{max_phases}")
        if len(c["steps"]) != c["phases"]:
            raise Fail(f"{t}: {len(c['steps'])} step values for {c['phases']} phases")
        if c["steps"][0] != 0:
            raise Fail(f"{t}: phase 0 must be the authored palette")
        if c["interval"] < MIN_INTERVAL:
            raise Fail(f"{t}: interval {c['interval']} < {MIN_INTERVAL} frames")
        for a, b in zip(c["steps"], c["steps"][1:] + c["steps"][:1]):  # includes the wrap
            if abs(a - b) > 1:
                raise Fail(f"{t}: step jumps {a}->{b} (>1 rung/unit per phase)")
        if c["mode"] == "TERRAIN_CYCLE_RAMP":
            if c["count"] < 2 or any(abs(s) > c["count"] - 1 for s in c["steps"]):
                raise Fail(f"{t}: ramp shift outside the ramp")
        else:
            if any(s < 0 or s > MAX_GLOW_UNITS for s in c["steps"]):
                raise Fail(f"{t}: glow outside 0..{MAX_GLOW_UNITS} units")
    return {c["terrain"]: c for c in cfgs}


def check_palettes(by_terrain):
    report = []
    for terrain, cfg in by_terrain.items():
        d, variants = TERRAINS[terrain]
        counts = sprite_counts(d)
        rng = range(cfg["first"], cfg["first"] + cfg["count"])
        for side, cnt in counts.items():
            drawn = sum(cnt[1:])
            body = max(range(1, 16), key=lambda i: cnt[i])
            used = sum(cnt[i] for i in rng)
            if body in rng:
                raise Fail(f"{terrain}/{side}: animates the dominant body index {body}")
            if used == 0:
                raise Fail(f"{terrain}/{side}: animated range has no pixels (nothing to support the effect)")
            if used / drawn > MAX_COVERAGE:
                raise Fail(f"{terrain}/{side}: animated range covers {used / drawn:.0%} of drawn pixels")
            if 0 in rng:
                raise Fail(f"{terrain}: animates the transparent index")
        for v in variants:
            pal = [to555(c) for c in load_pal(ROOT / TERRAIN_RES / d / f"{v}.pal")]
            base = [pal[i] for i in rng]
            for i in rng:
                if pal[i] == (0, 0, 0):
                    raise Fail(f"{terrain}/{v}: animated entry {i} is a black outline/shadow entry")
            if cfg["mode"] == "TERRAIN_CYCLE_RAMP":
                ls = [lum(c) for c in base]
                if not (all(a < b for a, b in zip(ls, ls[1:])) or all(a > b for a, b in zip(ls, ls[1:]))):
                    raise Fail(f"{terrain}/{v}: ramp entries are not monotone in luminance")
            frames = [phase_colors(cfg, base, s) for s in range(cfg["phases"])]
            if frames[0] != base:
                raise Fail(f"{terrain}/{v}: phase 0 differs from the authored colours")
            worst_step = worst_peak = 0.0
            for s in range(cfg["phases"]):
                nxt = frames[(s + 1) % cfg["phases"]]
                for a, b in zip(frames[s], nxt):
                    worst_step = max(worst_step, abs(lum(a) - lum(b)))
                    if cfg["mode"] == "TERRAIN_CYCLE_GLOW" and max(abs(x - y) for x, y in zip(a, b)) > GLOW_STEP_UNITS:
                        raise Fail(f"{terrain}/{v}: glow step exceeds {GLOW_STEP_UNITS} unit/channel")
                for a, b in zip(frames[s], base):
                    worst_peak = max(worst_peak, abs(lum(a) - lum(b)))
            if worst_step > MAX_STEP_LUM:
                raise Fail(f"{terrain}/{v}: per-step luminance change {worst_step:.3f} > {MAX_STEP_LUM}")
            if worst_peak > MAX_PEAK_LUM:
                raise Fail(f"{terrain}/{v}: peak luminance drift {worst_peak:.3f} > {MAX_PEAK_LUM}")
            if cfg["mode"] == "TERRAIN_CYCLE_GLOW":
                # a glowing entry must never outshine the lightest surface colour (>= 5% of the
                # drawn pixels) of either sprite, so speckles/cracks stay detail, not highlights
                for side, cnt in counts.items():
                    drawn = sum(cnt[1:])
                    surface = [i for i in range(1, 16) if cnt[i] / drawn >= 0.05 and i not in rng]
                    ceiling = max(lum(pal[i]) for i in surface)
                    for fr in frames:
                        if any(lum(c) > ceiling for c in fr):
                            raise Fail(f"{terrain}/{v}/{side}: glow outshines the lightest surface colour")
            report.append(f"{terrain}/{v}: step<={worst_step:.3f} peak<={worst_peak:.3f}")
    return report


def check_time_of_day_wiring(c_src):
    """'all' terrains must feed the same authored palette for every time of day."""
    for terrain, (d, variants) in TERRAINS.items():
        if variants == ["all"]:
            mb = read(f"{TERRAIN_RES}/{d}/meson.build")
            if "all.pal" not in mb or "day.pal" in mb:
                raise Fail(f"{d}: expected a single all.pal source")
        else:
            mb = read(f"{TERRAIN_RES}/{d}/meson.build")
            for v in variants:
                if f"'{v}.pal'" not in mb:
                    raise Fail(f"{d}: {v}.pal missing from meson.build")


def func_body(src, name):
    m = re.search(r"\n(?:static )?\w[\w \*]*\b" + re.escape(name) + r"\([^)]*\)\n\{(.*?)\n\}\n", src, re.S)
    if not m:
        raise Fail(f"function {name} not found")
    return m.group(1)


def check_source(c_src, h_src, main_src):
    cycle_part = c_src[c_src.index("IO-PAL-CYCLE"):c_src.index("void Terrain_LoadResources")]
    if c_src.count("SysTask_Start(") != 1:
        raise Fail("terrain.c must create exactly one SysTask")
    if len(re.findall(r"SysTask_Start\(\s*SysTask_CycleTerrainPalette", c_src)) != 1:
        raise Fail("cycle task is not created through SysTask_CycleTerrainPalette")
    if re.search(r"Heap_Alloc|Heap_Create|Malloc|NNS_FndAlloc|SysTask_Start.*\n.*SysTask_Start", cycle_part):
        raise Fail("cycle code allocates")
    start = func_body(c_src, "Terrain_StartPaletteCycle")
    for needle in ("terrain->paletteTask != NULL", "objPaletteIdx == TERRAIN_OBJ_PALETTE_NONE",
                   "objPaletteIdx >= 16", "config == NULL", "SysTask_Start("):
        if needle not in start:
            raise Fail(f"Terrain_StartPaletteCycle lacks guard/step: {needle}")
    if start.index("config == NULL") > start.index("SysTask_Start("):
        raise Fail("task created before the config check")
    find = func_body(c_src, "Terrain_FindCycleConfig")
    for needle in ("config->count == 0", "TERRAIN_CYCLE_MAX_COLORS", "firstIdx + config->count > 16",
                   "TERRAIN_CYCLE_MAX_PHASES", "interval == 0", "steps[0] != 0", "return NULL"):
        if needle not in find:
            raise Fail(f"Terrain_FindCycleConfig lacks sanity check: {needle}")
    task = func_body(c_src, "SysTask_CycleTerrainPalette")
    if "BattleSystem_GetRenderMode(battleSys) != 0" not in task:
        raise Fail("task ignores the render mode")
    if "PaletteData_GetSelectedBuffersMask(paletteData) & (PLTTBUF_MAIN_OBJ_F | PLTTBUF_MAIN_BG_F)" not in task:
        raise Fail("task ignores fades on OBJ/BG")
    if task.index("GetSelectedBuffersMask") > task.index("Terrain_WriteCycleColors"):
        raise Fail("fade check must precede any write")
    if "PLTTBUF_MAIN_OBJ, terrain->objPaletteIdx" not in task or "PLTTBUF_MAIN_BG, TERRAIN_BG_PALETTE_SLOT" not in task:
        raise Fail("OBJ and BG slot 7 mirror must both be written")
    if task.index("PLTTBUF_MAIN_OBJ, terrain->objPaletteIdx") > task.index("PLTTBUF_MAIN_BG, TERRAIN_BG_PALETTE_SLOT"):
        raise Fail("OBJ must be written before the BG mirror")
    if "terrain->cycleStep = nextStep" not in task or task.index("return;\n    }\n\n    // Keep") > task.index("cycleStep = nextStep"):
        raise Fail("phase must only advance after a successful OBJ write")
    write = func_body(c_src, "Terrain_WriteCycleColors")
    if "Terrain_RangeEquals(faded, unfaded, count) == FALSE" not in write:
        raise Fail("write lacks faded==unfaded ownership check")
    if write.index("Terrain_RangeEquals(faded") > write.index("MI_CpuCopy16(newColors"):
        raise Fail("ownership check must precede the copy")
    if "terrain->cycleBaseColors, count) == FALSE" not in write:
        raise Fail("write lacks base/current ownership check")
    if "u32 start = PLTT_DEST(paletteIdx) + config->firstIdx;" not in write or "u32 hwOffset = PLTT_OFFSET(paletteIdx) + config->firstIdx * sizeof(u16);" not in write or "u32 size = count * sizeof(u16);" not in write:
        raise Fail("write not confined to the configured range")
    if len(re.findall(r"MI_CpuCopy16\(newColors", write)) != 2 or "GX_Load" not in write:
        raise Fail("write path changed unexpectedly")
    if re.findall(r"GX_Load\w+\(", c_src).__len__() != 2:
        raise Fail("unexpected direct hardware palette writes in terrain.c")
    stop = func_body(c_src, "Terrain_StopPaletteCycle")
    for needle in ("paletteTask == NULL", "SysTask_Done(terrain->paletteTask)", "paletteTask = NULL",
                   "cycleStep != 0", "GetSelectedBuffersMask", "cycleStep = 0"):
        if needle not in stop:
            raise Fail(f"Terrain_StopPaletteCycle lacks: {needle}")
    if "Terrain_StopPaletteCycle(terrain)" not in func_body(c_src, "Terrain_Destroy"):
        raise Fail("Terrain_Destroy does not stop the cycle")
    if "MI_CpuClearFast(terrain, sizeof(Terrain))" not in func_body(c_src, "Terrain_Init"):
        raise Fail("Terrain_Init must clear state")
    if not re.search(r"Terrain_StopPaletteCycle\(&battleSys->terrains\[0\]\);\s*Terrain_StopPaletteCycle\(&battleSys->terrains\[1\]\);", main_src):
        raise Fail("battle exit does not stop both terrain cycles")
    if "Terrain_StartPaletteCycle(terrain, BattleSystem_GetPaletteData(terrain->battleSys), objPaletteIdx)" not in c_src:
        raise Fail("cycle is not started from Terrain_LoadResources with the allocated palette index")
    if "TERRAIN_CYCLE_MAX_COLORS" not in h_src or "const TerrainCycleConfig *cycleConfig" not in h_src:
        raise Fail("header lacks cycle state")


def check_regression(cfgs, c_src):
    names = sorted(c["terrain"] for c in cfgs)
    if names != sorted(TERRAINS):
        raise Fail(f"animated terrain set changed: {names}")
    water = next(c for c in cfgs if c["terrain"] == "TERRAIN_WATER")
    pilot = dict(mode="TERRAIN_CYCLE_RAMP", first=4, count=4, interval=16, phases=4, steps=[0, 1, 0, -1])
    for k, v in pilot.items():
        if water[k] != v:
            raise Fail(f"water pilot parameter {k} changed: {water[k]} != {v}")
    for sym in ("sTerrainSpriteSource_PlayerSide", "sTerrainPaletteSource", "Terrain_CreateSprite",
                "Terrain_UnloadResources"):
        if sym not in c_src:
            raise Fail(f"{sym} missing")


def check_assets_unchanged():
    try:
        subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", BASELINE + "^{commit}"], check=True,
                       capture_output=True)
    except (OSError, subprocess.CalledProcessError):
        return "skipped (baseline commit not available)"
    r = subprocess.run(["git", "-C", str(ROOT), "diff", "--stat", BASELINE, "--", TERRAIN_RES],
                       capture_output=True, text=True)
    if r.stdout.strip():
        raise Fail("terrain art/palettes changed vs baseline:\n" + r.stdout)
    return "unchanged vs " + BASELINE[:8]


# ---------------------------------------------------------------- driver
def run_all(c_src, h_src, main_src):
    max_phases, max_colors = parse_limits(c_src, h_src)
    cfgs = parse_configs(c_src)
    by_terrain = check_configs(cfgs, max_phases, max_colors)
    rep = check_palettes(by_terrain)
    check_time_of_day_wiring(c_src)
    check_source(c_src, h_src, main_src)
    check_regression(cfgs, c_src)
    return cfgs, rep


def mutations(c, h, m):
    def sub(s, a, b, n=1):
        if a not in s:
            raise Fail(f"mutation anchor missing: {a!r}")
        return s.replace(a, b, n)

    return {
        "ice animates dominant body index": (sub(c, "TERRAIN_ICE,              TERRAIN_CYCLE_RAMP,  9, 3", "TERRAIN_ICE,              TERRAIN_CYCLE_RAMP,  8, 3"), h, m),
        "range runs past entry 15": (sub(c, "TERRAIN_CAVE,             TERRAIN_CYCLE_GLOW, 10, 1", "TERRAIN_CAVE,             TERRAIN_CYCLE_GLOW, 15, 2"), h, m),
        "animates transparent entry": (sub(c, "TERRAIN_WATER,            TERRAIN_CYCLE_RAMP,  4, 4", "TERRAIN_WATER,            TERRAIN_CYCLE_RAMP,  0, 4"), h, m),
        "flicker interval": (sub(c, "TERRAIN_WATER,            TERRAIN_CYCLE_RAMP,  4, 4, 16, 4", "TERRAIN_WATER,            TERRAIN_CYCLE_RAMP,  4, 4, 4, 4"), h, m),
        "water pilot altered": (sub(c, "{ 0, 1, 0, -1 }", "{ 0, 1, 1, -1 }"), h, m),
        "phase 0 not authored": (sub(c, "{ 0, 1, 2, 3, 2, 1, 0, 0 }", "{ 1, 1, 2, 3, 2, 1, 0, 0 }"), h, m),
        "glow too strong": (sub(c, "{ 0, 1, 2, 3, 2, 1, 0, 0 }", "{ 0, 1, 2, 3, 4, 5, 4, 3 }"), h, m),
        "glow jumps": (sub(c, "{ 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 0, 0 }", "{ 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0 }"), h, m),
        "ramp wraps around": (sub(c, "{ 0, 1, 1, 0, -1, -1 }", "{ 0, 1, 2, 0, -1, -1 }"), h, m),
        "extra terrain animated": (sub(c, "    { TERRAIN_CAVE,", "    { TERRAIN_SNOW,             TERRAIN_CYCLE_RAMP,  9, 3, 20, 2,  { 0, 1 } },\n    { TERRAIN_CAVE,"), h, m),
        "second task": (sub(c, "terrain->cycleTimer = 0;\n    terrain->cycleStep = 0;\n    terrain->paletteTask", "terrain->cycleTimer = 0;\n    terrain->cycleStep = 0;\n    SysTask_Start(SysTask_CycleTerrainPalette, terrain, 1);\n    terrain->paletteTask"), h, m),
        "fade guard removed": (sub(c, "(PLTTBUF_MAIN_OBJ_F | PLTTBUF_MAIN_BG_F)) {\n        return;", "(0)) {\n        return;"), h, m),
        "render mode guard removed": (sub(c, "BattleSystem_GetRenderMode(battleSys) != 0", "FALSE"), h, m),
        "ownership check removed": (sub(c, "Terrain_RangeEquals(faded, unfaded, count) == FALSE", "FALSE"), h, m),
        "BG mirror dropped": (sub(c, "Terrain_WriteCycleColors(terrain, paletteData, PLTTBUF_MAIN_BG, TERRAIN_BG_PALETTE_SLOT, curColors, newColors);\n    terrain->cycleStep", "terrain->cycleStep"), h, m),
        "no-palette guard removed": (sub(c, "|| objPaletteIdx >= 16", ""), h, m),
        "config check removed": (sub(c, "config == NULL", "FALSE", 1), h, m),
        "sanity check removed": (sub(c, "|| config->interval == 0", ""), h, m),
        "destroy leaks task": (sub(c, "void Terrain_Destroy(Terrain *terrain)\n{\n    Terrain_StopPaletteCycle(terrain);\n", "void Terrain_Destroy(Terrain *terrain)\n{\n"), h, m),
        "battle exit leaks task": (c, h, sub(m, "Terrain_StopPaletteCycle(&battleSys->terrains[1]);", "")),
        "stop never frees task": (sub(c, "SysTask_Done(terrain->paletteTask);", ""), h, m),
        "write outside range": (sub(c, "PLTT_OFFSET(paletteIdx) + config->firstIdx * sizeof(u16)", "PLTT_OFFSET(paletteIdx)"), h, m),
        "allocation added": (sub(c, "u16 curColors[TERRAIN_CYCLE_MAX_COLORS];\n    u16 newColors", "void *x = Heap_Alloc(HEAP_ID_BATTLE, 16);\n    u16 curColors[TERRAIN_CYCLE_MAX_COLORS];\n    u16 newColors"), h, m),
    }


def main():
    c, h, m = read("src/battle/terrain.c"), read("include/battle/terrain.h"), read("src/battle/battle_main.c")
    cfgs, rep = run_all(c, h, m)
    print(f"OK: {len(cfgs)} terrain configs validated: " + ", ".join(x['terrain'] for x in cfgs))
    for line in rep:
        print("  " + line)
    print("  assets: " + check_assets_unchanged())
    if "--no-mutations" in sys.argv:
        return 0
    survived = []
    muts = mutations(c, h, m)
    for name, (mc, mh, mm) in muts.items():
        try:
            run_all(mc, mh, mm)
        except (Fail, ValueError, IndexError, AttributeError):
            continue
        survived.append(name)
    print(f"mutation self-test: {len(muts) - len(survived)}/{len(muts)} defects rejected")
    if survived:
        print("SURVIVING MUTATIONS: " + ", ".join(survived))
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Fail as e:
        print("FAIL: " + str(e))
        sys.exit(1)
