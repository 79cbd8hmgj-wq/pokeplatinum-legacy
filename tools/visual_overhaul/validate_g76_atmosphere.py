#!/usr/bin/env python3
"""Validate the G7.6 overworld atmosphere pass against its pinned baseline.

Checks
  * only the intended texture sets / lighting sets / area records changed;
  * graded textures keep names, dimensions and every texel index (palette-only);
  * lighting keyframe structure (times, enable flags, directions) is unchanged;
  * every consumer of a graded/new resource belongs to the intended family;
  * no map geometry, collision, script, event, matrix or encounter data changed;
  * the outdoors-lighting classification covers every outdoor lighting ID.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_g76_atmosphere as gen  # noqa: E402

ROOT = gen.ROOT
BASE = gen.BASE_REV

FROZEN_PREFIXES = (
    "res/field/maps/data/",
    "res/field/matrices/",
    "res/field/scripts/",
    "res/field/events/",
    "res/field/encounters/",
    "res/field/props/",
    "include/data/map_headers.h",
)

# lighting set -> area records allowed to reference it after G7.6
EXPECTED_LIGHT_USERS = {
    "lighting_set_006": {"area_data_058", "area_data_068", "area_data_077"},
    "lighting_set_007": {"area_data_069"},
    "lighting_set_009": {"area_data_074"},
    "lighting_set_010": {"area_data_075"},
    "lighting_set_011": {"area_data_014"},
    "lighting_set_012": {"area_data_060"},
    "lighting_set_013": {"area_data_062"},
    "lighting_set_014": {"area_data_076"},
    "lighting_set_015": {"area_data_053", "area_data_055", "area_data_056", "area_data_057", "area_data_071"},
    "lighting_set_016": {"area_data_070"},
    "lighting_set_017": {"area_data_013"},
    "lighting_set_018": {"area_data_015"},
    "lighting_set_019": {"area_data_018"},
}

# graded texture set -> area records that may consume it (shared-consumer audit)
EXPECTED_TEX_USERS = {
    "map_texture_set_074": {"area_data_075"},
    "map_texture_set_014": {"area_data_014"},
    "map_texture_set_057": {"area_data_058"},
    "map_texture_set_067": {"area_data_068"},
    "map_texture_set_076": {"area_data_077"},
    "map_texture_set_068": {"area_data_069"},
    "map_texture_set_069": {"area_data_070"},
    "map_texture_set_059": {"area_data_060"},
    "map_texture_set_073": {"area_data_074"},
    "map_texture_set_061": {"area_data_062"},
    "map_texture_set_013": {"area_data_013"},
    "map_texture_set_015": {"area_data_015"},
    "map_texture_set_018": {"area_data_018"},
    "map_texture_set_052": {"area_data_053"},
    "map_texture_set_054": {"area_data_055"},
    "map_texture_set_055": {"area_data_056"},
    "map_texture_set_056": {"area_data_057"},
    "map_texture_set_070": {"area_data_071"},
    "map_texture_set_075": {"area_data_076"},
}

errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def build_dump_tool(tmp: Path) -> Path:
    nb = ROOT / "tools/nitrobtx"
    srcs = ["src/common.c", "src/ns/chunks/tex.c", "src/ns/container.c", "src/ns/resource_dict.c",
            "src/ns/resource_name.c", "src/ns/resource_tree.c", "src/palette.c", "src/texture.c",
            "src/help.c", "src/options.c", "src/main.c"]
    exe = tmp / "nitrobtx"
    subprocess.run(["gcc", "-std=gnu17", "-O2", f"-I{nb / 'include'}", *(str(nb / s) for s in srcs),
                    "-lpng", "-lm", "-o", str(exe)], check=True)
    return exe


def dump(exe: Path, nsbtx: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(exe), "dump", str(nsbtx), str(out)], check=True, capture_output=True)


def check_scope() -> None:
    changed = git("diff", "--name-only", BASE, "--").split()
    for path in changed:
        if path.startswith(FROZEN_PREFIXES):
            fail(f"frozen gameplay/geometry data changed: {path}")
    allowed_tex = {f"{gen.TEX_DIR}/{n}.nsbtx" for n in gen.TEXTURE_JOBS}
    for path in changed:
        if path.startswith(gen.TEX_DIR + "/") and path not in allowed_tex:
            fail(f"unexpected texture set changed: {path}")
    untracked = git("ls-files", "--others", "--exclude-standard", gen.TEX_DIR).split()
    if untracked:
        fail(f"unexpected new texture files: {untracked}")


def check_textures(tmp: Path) -> int:
    exe = build_dump_tool(tmp)
    report = json.loads(gen.REPORT.read_text())
    graded_palettes = 0
    for tex in gen.TEXTURE_JOBS:
        before_file = tmp / f"{tex}.base.nsbtx"
        before_file.write_bytes(gen.git_blob(f"{gen.TEX_DIR}/{tex}.nsbtx"))
        before_dir, after_dir = tmp / "b" / tex, tmp / "a" / tex
        dump(exe, before_file, before_dir)
        dump(exe, ROOT / gen.TEX_DIR / f"{tex}.nsbtx", after_dir)

        b_png = {p.name for p in before_dir.glob("*.png")}
        a_png = {p.name for p in after_dir.glob("*.png")}
        b_pal = {p.name for p in before_dir.glob("*.pal")}
        a_pal = {p.name for p in after_dir.glob("*.pal")}
        if b_png != a_png or b_pal != a_pal:
            fail(f"{tex}: texture/palette name set changed")
            continue
        for name in sorted(b_png):
            with Image.open(before_dir / name) as x, Image.open(after_dir / name) as y:
                if x.size != y.size:
                    fail(f"{tex}/{name}: dimensions changed")
                elif x.mode == "P" and y.mode == "P" and x.tobytes() != y.tobytes():
                    fail(f"{tex}/{name}: texel indices changed")
        changed = {p[:-4] for p in b_pal if (before_dir / p).read_text() != (after_dir / p).read_text()}
        expected = set(report["textures"][tex]["palettes"])
        if changed != expected:
            fail(f"{tex}: changed palettes {sorted(changed ^ expected)} disagree with generator report")
        if not changed:
            fail(f"{tex}: no palette changed")
        graded_palettes += len(changed)
    return graded_palettes


def check_lighting() -> None:
    sets = {**{k: v[0] for k, v in gen.LIGHTING_INPLACE.items()}, **{k: v[0] for k, v in gen.LIGHTING_NEW.items()}}
    for name, src in sets.items():
        new = json.loads((ROOT / gen.LIGHT_DIR / f"{name}.json").read_text())
        old = gen.base_json(f"{gen.LIGHT_DIR}/{src}.json")
        if len(new) != len(old):
            fail(f"{name}: keyframe count changed")
            continue
        for i, (n, o) in enumerate(zip(new, old)):
            if n["endTime"] != o["endTime"]:
                fail(f"{name}[{i}]: endTime changed")
            for j, (ln, lo) in enumerate(zip(n["lights"], o["lights"])):
                if ln["enabled"] != lo["enabled"] or ln["direction"] != lo["direction"]:
                    fail(f"{name}[{i}] light {j}: enable flag/direction changed")
                if not ln["enabled"] and any(ln["color"].values()):
                    fail(f"{name}[{i}] light {j}: disabled light not black")
                for ch, v in ln["color"].items():
                    if not 0 <= v <= 31:
                        fail(f"{name}[{i}] light {j}: {ch}={v} out of range")
            for field in ("diffuseColor", "ambientColor", "specularColor", "emissionColor"):
                for ch, v in n[field].items():
                    if not 0 <= v <= 31:
                        fail(f"{name}[{i}] {field}.{ch}={v} out of range")
                # silhouette floor: never let ambient+diffuse collapse
            floor = min(n["diffuseColor"].values()) + min(n["ambientColor"].values())
            if floor < 6:
                fail(f"{name}[{i}]: ambient+diffuse floor {floor} would crush shadows")
    # untouched sets must be byte-identical to base
    for path in sorted((ROOT / gen.LIGHT_DIR).glob("lighting_set_*.json")):
        if path.stem in sets:
            continue
        if path.read_bytes() != gen.git_blob(f"{gen.LIGHT_DIR}/{path.name}"):
            fail(f"{path.name}: shared lighting set changed unexpectedly")


def check_area_data() -> None:
    users_light: dict[str, set[str]] = {}
    users_tex: dict[str, set[str]] = {}
    for path in sorted((ROOT / gen.AREA_DIR).glob("area_data_*.json")):
        cur = json.loads(path.read_text())
        old = gen.base_json(f"{gen.AREA_DIR}/{path.name}")
        diff = {k for k in cur if cur[k] != old.get(k)}
        if path.stem in gen.AREA_LIGHT_REPOINT:
            if diff - {"lightingSet"}:
                fail(f"{path.name}: fields other than lightingSet changed: {sorted(diff)}")
        elif diff:
            fail(f"{path.name}: unexpected area-data change {sorted(diff)}")
        users_light.setdefault(cur["lightingSet"], set()).add(path.stem)
        users_tex.setdefault(cur["mapTextureSet"], set()).add(path.stem)
    for lighting, expected in EXPECTED_LIGHT_USERS.items():
        if users_light.get(lighting, set()) != expected:
            fail(f"{lighting}: consumers {sorted(users_light.get(lighting, set()))} != expected {sorted(expected)}")
    for tex, expected in EXPECTED_TEX_USERS.items():
        if users_tex.get(tex, set()) != expected:
            fail(f"{tex}: consumers {sorted(users_tex.get(tex, set()))} != expected {sorted(expected)}")


def check_outdoors_contract() -> None:
    header = (ROOT / "include/constants/field/area_light.h").read_text()
    ids = re.findall(r"^\s+(AREA_LIGHT_SET_\w+?)(?:\s*=\s*\d+)?,", header, re.M)
    order = [x for x in (ROOT / gen.LIGHT_DIR / "lighting_sets.order").read_text().split() if x]
    if len(ids) - 1 != len(order):
        fail(f"enum has {len(ids) - 1} named sets, lighting archive has {len(order)}")
    src = (ROOT / "src/overlay005/area_data.c").read_text()
    body = src.split("AreaDataManager_IsOutdoorsLighting", 1)[1].split("default:", 1)[0]
    outdoors = set(re.findall(r"case (AREA_LIGHT_SET_\w+):", body))
    # Every set derived from an outdoor retail set (000, 004, 005, 008) must
    # keep the outdoors classification so terrain stays on the global light.
    derived = {
        "lighting_set_010": "AREA_LIGHT_SET_ETERNA_FOREST_GRADE",
        "lighting_set_011": "AREA_LIGHT_SET_SNOW_REGION_GRADE",
        "lighting_set_012": "AREA_LIGHT_SET_SPEAR_PILLAR_GRADE",
        "lighting_set_013": "AREA_LIGHT_SET_SINNOH_LAKES",
        "lighting_set_017": "AREA_LIGHT_SET_COAST_RESORT",
        "lighting_set_018": "AREA_LIGHT_SET_COAST_HARBOR",
        "lighting_set_019": "AREA_LIGHT_SET_LAKESHORE",
    }
    for lighting, name in derived.items():
        if name not in outdoors:
            fail(f"{lighting}: {name} missing from IsOutdoorsLighting")
        if ids[int(lighting[-3:])] != name:
            fail(f"{lighting}: enum slot {int(lighting[-3:])} is {ids[int(lighting[-3:])]}, expected {name}")
    for name in ("AREA_LIGHT_SET_CAVE_NATURAL", "AREA_LIGHT_SET_MT_CORONET_UPPER"):
        if name in outdoors:
            fail(f"{name} must remain an indoor/cave classification")
    for lighting, name in (("lighting_set_015", "AREA_LIGHT_SET_CAVE_NATURAL"),
                           ("lighting_set_016", "AREA_LIGHT_SET_MT_CORONET_UPPER")):
        if ids[int(lighting[-3:])] != name:
            fail(f"{lighting}: enum slot is {ids[int(lighting[-3:])]}, expected {name}")


def main() -> int:
    check_scope()
    check_lighting()
    check_area_data()
    check_outdoors_contract()
    with tempfile.TemporaryDirectory() as tmp:
        palettes = check_textures(Path(tmp))
    if errors:
        print("\n".join(f"FAIL: {e}" for e in errors))
        return 1
    print(f"PASS: {len(gen.TEXTURE_JOBS)} texture sets ({palettes} palettes) palette-only; "
          f"{len(gen.LIGHTING_INPLACE) + len(gen.LIGHTING_NEW)} lighting sets structure-preserving; "
          f"{len(gen.AREA_LIGHT_REPOINT)} area records re-pointed (lightingSet only); "
          "no geometry/collision/script/event/encounter data changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
