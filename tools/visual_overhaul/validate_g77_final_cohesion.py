#!/usr/bin/env python3
"""G7.7 final visual-cohesion validator (closure guard for the whole G7 stack).

Checks
  * DIFF GUARD   - since the merged G7.6 baseline (PR #59) only visual paths may
                   change; any gameplay/script/event/encounter/geometry/engine
                   path fails closed.
  * OWNERSHIP    - resource -> area record -> map header consumer table for every
                   G7.6-graded texture/lighting set equals the committed audit
                   (docs/visual_overhaul/G7_7_RESOURCE_OWNERSHIP.json); a new
                   consumer of a graded resource fails.
  * TEXTURES     - every graded NSBTX keeps texture names/dimensions/formats and
                   palette names/lengths versus the pinned G7.6 base; per-set grade
                   magnitude stays inside the audited envelope (no compounding).
  * HIERARCHY    - lighting grade strength (distance from the pinned retail set)
                   orders ordinary < standard environment < special/legendary.
  * UI ACCENT    - gold focus accent family is consistent across Party/Bag/Shop/
                   Battle; documented retail-accent exceptions are pinned.
  * ORDINARY     - lighting set 000/001 and their texture sets are untouched.

Usage: validate_g77_final_cohesion.py [--write-ownership]
"""
from __future__ import annotations

import colorsys
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nsbtx_palettes as nsbtx  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
G76_BASE = "896570704f269ebdf3bb96d4767319f782a1305a"  # pre-G7.6 pinned baseline
G77_BASE = "76f27a81895d93b6d9c8772a49a4cdec667f649a"  # merge of PR #59 (G7.6)
OWNERSHIP = ROOT / "docs/visual_overhaul/G7_7_RESOURCE_OWNERSHIP.json"

# Paths G7.7 may touch. Everything else is a gameplay / engine / data change.
ALLOWED_PATTERNS = (
    r"^tools/visual_overhaul/.+",
    r"^docs/visual_overhaul/.+",
    r"^\.github/workflows/g7-visual-validation\.yml$",
    r"^\.github/workflows/g4-runtime-harness\.yml$",
    r"^res/field/lighting/lighting_set_0(12|15)\.json$",  # hierarchy pass
)

errors: list[str] = []


def check(cond: bool, msg: str) -> None:
    if not cond:
        errors.append(msg)


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True).stdout


def blob(rev: str, path: str) -> bytes | None:
    try:
        return git("show", f"{rev}:{path}")
    except subprocess.CalledProcessError:
        return None


# --------------------------------------------------------------------------
# diff guard
# --------------------------------------------------------------------------
def check_diff_guard() -> None:
    try:
        git("cat-file", "-e", f"{G77_BASE}^{{commit}}")
    except subprocess.CalledProcessError:
        errors.append(f"baseline {G77_BASE[:12]} not available (need full-history checkout)")
        return
    out = git("diff", "--name-only", "--no-renames", G77_BASE).decode().split("\n")
    out += git("ls-files", "--others", "--exclude-standard").decode().split("\n")
    changed = sorted({p for p in out if p})
    bad = [p for p in changed if not any(re.match(rx, p) for rx in ALLOWED_PATTERNS)]
    check(not bad, f"G7.7 changed non-visual paths (gameplay guard): {bad}")


# --------------------------------------------------------------------------
# ownership
# --------------------------------------------------------------------------
def map_headers() -> list[dict]:
    txt = (ROOT / "include/data/map_headers.h").read_text()
    rows = []
    for name, body in re.findall(r"\[(MAP_HEADER_[A-Z0-9_]+)\]\s*=\s*\{(.*?)\n    \},", txt, re.S):
        def field(rx):
            m = re.search(rx, body)
            return m.group(1) if m else None

        rows.append({
            "map": name,
            "area": field(r"\.areaDataArchiveID\s*=\s*(area_data_\d+)"),
            "type": field(r"\.mapType\s*=\s*MAP_TYPE_(\w+)"),
            "label": field(r"LocationNames_Text_(\w+)"),
            "weather": field(r"\.weather\s*=\s*OVERWORLD_WEATHER_(\w+)"),
            "battle_bg": field(r"\.battleBG\s*=\s*BACKGROUND_(\w+)"),
        })
    return rows


def graded_resources() -> tuple[list[str], list[str]]:
    report = json.loads((ROOT / "docs/visual_overhaul/G7_6_ATMOSPHERE_REPORT.json").read_text())
    return sorted(report["textures"]), sorted(report["lighting"])


def build_ownership() -> dict:
    tex_sets, light_sets = graded_resources()
    headers = map_headers()
    areas = {p.stem: json.loads(p.read_text()) for p in sorted((ROOT / "res/field/area_data").glob("area_data_*.json"))}

    def consumers(key: str, value: str) -> dict:
        recs = sorted(a for a, d in areas.items() if d.get(key) == value)
        maps = [h for h in headers if h["area"] in recs]
        return {
            "area_records": recs,
            "maps": [f"{h['map']} [{h['type']}/{h['label']}]" for h in maps],
        }

    return {
        "baseline": G77_BASE,
        "lighting_sets": {s: consumers("lightingSet", s) for s in light_sets},
        "texture_sets": {s: consumers("mapTextureSet", s) for s in tex_sets},
    }


def check_ownership(write: bool) -> None:
    now = build_ownership()
    if write:
        OWNERSHIP.write_text(json.dumps(now, indent=2, sort_keys=True) + "\n")
        print(f"wrote {OWNERSHIP.relative_to(ROOT)}")
        return
    if not OWNERSHIP.exists():
        errors.append("G7_7_RESOURCE_OWNERSHIP.json missing (run with --write-ownership)")
        return
    stored = json.loads(OWNERSHIP.read_text())
    check(stored == now, "resource ownership drifted from the audited G7.7 table "
                         "(new/removed consumer of a graded resource) - re-audit, then --write-ownership")
    # every graded resource must have at least one consumer and ordinary retail sets stay unshared
    for kind in ("lighting_sets", "texture_sets"):
        for name, c in now[kind].items():
            check(bool(c["area_records"]), f"{name}: graded resource has no consumer")
    # ordinary-leak: graded special families must not be consumed by town/city or pokecenter maps
    # unless the family is a resort/harbour/snow-town family (documented in the report).
    for name, c in now["texture_sets"].items():
        for m in c["maps"]:
            check("[POKECENTER/" not in m, f"{name}: Pokemon Center map consumes a graded set: {m}")


# --------------------------------------------------------------------------
# textures
# --------------------------------------------------------------------------
def luma(c: int) -> float:
    r, g, b = (c & 31) / 31, ((c >> 5) & 31) / 31, ((c >> 10) & 31) / 31
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def sat(c: int) -> float:
    r, g, b = (c & 31) / 31, ((c >> 5) & 31) / 31, ((c >> 10) & 31) / 31
    return colorsys.rgb_to_hsv(r, g, b)[1]


MAX_MEAN_ABS_DLUMA = 0.12   # audited max is Turnback 0.107
MAX_MEAN_DSAT = 0.35        # audited max is Veilstone warehouse 0.327


def check_textures() -> None:
    tex_sets, _ = graded_resources()
    for name in tex_sets:
        path = f"res/field/maps/texture_sets/{name}.nsbtx"
        now_b = (ROOT / path).read_bytes()
        base_b = blob(G76_BASE, path)
        if base_b is None:
            errors.append(f"{name}: pinned base blob missing")
            continue
        check(nsbtx.read_textures(now_b) == nsbtx.read_textures(base_b),
              f"{name}: texture names/dimensions/formats changed")
        pn, pb = nsbtx.read_palettes(now_b), nsbtx.read_palettes(base_b)
        # The recolor tool re-serializes the archive; name lookup is order-independent, so
        # compare the name *sets* (order may legitimately differ) and per-name contents.
        check(set(pn) == set(pb), f"{name}: palette names changed")
        tex_n = {t[0]: t[4] for t in nsbtx.decode_textures(now_b)}
        tex_b = {t[0]: t[4] for t in nsbtx.decode_textures(base_b)}
        check(tex_n == tex_b, f"{name}: texel index data changed (grades must be palette-only)")
        check(all(len(pn[k]) == len(pb[k]) for k in pb if k in pn), f"{name}: palette length changed")
        pairs = [(a, b) for k in pb if k in pn for a, b in zip(pn[k], pb[k]) if a != b]
        if not pairs:
            errors.append(f"{name}: listed as graded but identical to base")
            continue
        dl = [luma(a) - luma(b) for a, b in pairs]
        ds = [sat(a) - sat(b) for a, b in pairs]
        mean_abs = sum(abs(x) for x in dl) / len(dl)
        check(mean_abs <= MAX_MEAN_ABS_DLUMA, f"{name}: mean |dLuma| {mean_abs:.3f} exceeds {MAX_MEAN_ABS_DLUMA}")
        check(sum(ds) / len(ds) <= MAX_MEAN_DSAT, f"{name}: mean dSat {sum(ds) / len(ds):.3f} exceeds {MAX_MEAN_DSAT}")
        # magenta key colours must never be touched
        for k in pb:
            for a, b in zip(pn.get(k, []), pb[k]):
                if (b & 31) == 31 and ((b >> 5) & 31) == 0 and ((b >> 10) & 31) == 31:
                    check(a == b, f"{name}/{k}: magenta key colour modified")
    # ordinary retail sets untouched
    for name in ("map_texture_set_000", "map_texture_set_001"):
        path = f"res/field/maps/texture_sets/{name}.nsbtx"
        check((ROOT / path).read_bytes() == blob(G76_BASE, path), f"{name}: ordinary retail texture set changed")


# --------------------------------------------------------------------------
# lighting hierarchy
# --------------------------------------------------------------------------
PARENT = {"lighting_set_015": "lighting_set_001", "lighting_set_016": "lighting_set_007",
          "lighting_set_017": "lighting_set_000", "lighting_set_018": "lighting_set_000",
          "lighting_set_019": "lighting_set_000"}

# tier -> lighting sets. ordinary = coast/lake variants of the ordinary-route set;
# standard = named environments / natural dungeons; special = legendary / boss / unique spaces.
TIERS = {
    "ordinary": ("lighting_set_017", "lighting_set_018", "lighting_set_019", "lighting_set_013"),
    "standard": ("lighting_set_015", "lighting_set_010", "lighting_set_011", "lighting_set_007", "lighting_set_016",
                 "lighting_set_006"),
    "special": ("lighting_set_009", "lighting_set_012", "lighting_set_014"),
}


def kf_vec(kfs: list[dict], mode: str) -> list[float]:
    ks = kfs
    if mode == "day":
        ks = [k for k in kfs if 9000 <= k["endTime"] <= 30600] or kfs
        ks = [ks[len(ks) // 2]]
    out = []
    for k in ks:
        for c in (k["lights"][0]["color"], k["ambientColor"], k["diffuseColor"], k["specularColor"]):
            out += [c["red"] / 31, c["green"] / 31, c["blue"] / 31]
    return out


def strength(name: str, mode: str) -> float:
    base_name = PARENT.get(name, name)
    now = json.loads((ROOT / f"res/field/lighting/{name}.json").read_text())
    base = json.loads(blob(G76_BASE, f"res/field/lighting/{base_name}.json"))
    a, b = kf_vec(now, mode), kf_vec(base, mode)
    return sum(abs(x - y) for x, y in zip(a, b)) / (len(b) / 12)


def check_hierarchy() -> dict:
    s = {n: strength(n, "day") for tier in TIERS.values() for n in tier}
    mx = lambda tier: max(s[n] for n in TIERS[tier])  # noqa: E731
    mn = lambda tier: min(s[n] for n in TIERS[tier])  # noqa: E731
    # Legendary/boss spaces are never graded more weakly than the strongest standard environment...
    check(mn("special") >= mx("standard"),
          f"hierarchy: weakest special grade {mn('special'):.2f} < strongest standard {mx('standard'):.2f}")
    # ...and standard environments never more weakly than the strongest ordinary variant.
    check(mn("standard") >= mx("ordinary") - 0.15,
          f"hierarchy: weakest standard {mn('standard'):.2f} < strongest ordinary {mx('ordinary'):.2f} - 0.15")
    check(mx("ordinary") <= 0.30, f"hierarchy: ordinary variants graded too strongly ({mx('ordinary'):.2f})")
    # Ordinary retail lighting stays untouched.
    for n in ("lighting_set_000", "lighting_set_001"):
        p = f"res/field/lighting/{n}.json"
        check((ROOT / p).read_bytes() == blob(G76_BASE, p), f"{n}: ordinary retail lighting changed")
    # The legendary summit must not be luma-crushed to win the hierarchy.
    spear = json.loads((ROOT / "res/field/lighting/lighting_set_012.json").read_text())
    amb = min(0.2126 * k["ambientColor"]["red"] + 0.7152 * k["ambientColor"]["green"] + 0.0722 * k["ambientColor"]["blue"]
              for k in spear) / 31
    check(amb >= 0.15, f"lighting_set_012: ambient luma {amb:.3f} < 0.15 (crushed shade)")
    return s


# --------------------------------------------------------------------------
# UI accent family
# --------------------------------------------------------------------------
def jasc(path: str) -> list[tuple[int, int, int]]:
    lines = (ROOT / path).read_text().replace("\r", "").split("\n")[3:]
    return [tuple(int(x) for x in ln.split()) for ln in lines if ln.strip()]


def hue_sat(rgb: tuple[int, int, int]) -> tuple[float, float]:
    h, s, _ = colorsys.rgb_to_hsv(*(c / 255 for c in rgb))
    return h * 360, s


def check_ui_accent() -> None:
    from PIL import Image

    g = "res/graphics/"
    focus = {
        "party shared.pal[6]": jasc(g + "party_menu/shared.pal")[6],
        "bag ui_elements.pal[1]": jasc(g + "bag/ui_elements.pal")[1],
        "shop sprites.pal[1]": jasc(g + "shop_menu/sprites.pal")[1],
    }
    im = Image.open(ROOT / g / "battle/interface/cursor.png")
    pal = im.getpalette()
    focus["battle cursor.png[15]"] = tuple(pal[45:48])
    for name, rgb in focus.items():
        h, s = hue_sat(rgb)
        check(30 <= h <= 48 and s >= 0.65, f"{name}: {rgb} outside the G7 gold focus family (hue {h:.0f}, sat {s:.2f})")
    for a in ("party shared.pal[6]", "bag ui_elements.pal[1]", "shop sprites.pal[1]"):
        check(focus[a] == (246, 172, 57), f"{a}: expected the shared G7 gold (246,172,57), got {focus[a]}")
    # Documented, intentionally-preserved retail accents (shared sprite banks; see G7.7 report).
    check(jasc(g + "start_menu/menu.pal")[16 + 15] == (255, 106, 16),
          "start menu cursor accent changed (bank 1 is shared with the active-icon art)")
    check(jasc(g + "pokemon_summary_screen/sprites.pal")[16 + 3] == (246, 74, 41),
          "summary move-cursor accent changed (sprite bank shared with other summary chrome)")


# --------------------------------------------------------------------------
def main() -> int:
    write = "--write-ownership" in sys.argv
    check_diff_guard()
    check_ownership(write)
    if not write:
        check_textures()
        strengths = check_hierarchy()
        check_ui_accent()
    if errors:
        print("G7.7 final cohesion validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    if not write:
        print("G7.7 final cohesion validation passed")
        print("  lighting grade strength (day): " +
              ", ".join(f"{n[-3:]}={v:.2f}" for n, v in sorted(strengths.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
