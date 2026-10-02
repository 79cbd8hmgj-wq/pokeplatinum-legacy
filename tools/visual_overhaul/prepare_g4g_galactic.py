#!/usr/bin/env python3
"""Prepare isolated Team Galactic warehouse resources for the G4G environment pass."""
from __future__ import annotations
import json
import re
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

def add_order(path: Path, entry: str) -> None:
    lines=[x for x in path.read_text().splitlines() if x]
    if entry not in lines:
        lines.append(entry)
        path.write_text("\n".join(lines)+"\n")

def add_meson_entry(path: Path, anchor: str, entries: list[str]) -> None:
    lines=path.read_text().splitlines()
    missing=[e for e in entries if not any(f"'{e}'" in line for line in lines)]
    if not missing:
        return
    matches=[i for i,line in enumerate(lines) if f"'{anchor}'" in line]
    if len(matches)!=1:
        raise SystemExit(f"{path}: expected one anchor {anchor!r}, found {len(matches)}")
    idx=matches[0]
    if not lines[idx].rstrip().endswith(","):
        lines[idx]=lines[idx].rstrip()+","
    lines[idx+1:idx+1]=[f"    '{e}'," for e in missing]
    path.write_text("\n".join(lines)+"\n")

warehouse_area=ROOT/"res/field/area_data/area_data_077.json"
warehouse_tex=ROOT/"res/field/maps/texture_sets/map_texture_set_076.nsbtx"
if warehouse_area.exists() or warehouse_tex.exists():
    raise SystemExit("G4G warehouse isolation already exists; refusing to overwrite")

data=json.loads((ROOT/"res/field/area_data/area_data_031.json").read_text())
if data["mapTextureSet"]!="map_texture_set_030":
    raise SystemExit("area_data_031 no longer points at texture set 030")
data["mapTextureSet"]="map_texture_set_076"
warehouse_area.write_text(json.dumps(data,indent=4)+"\n")
shutil.copyfile(ROOT/"res/field/maps/texture_sets/map_texture_set_030.nsbtx",warehouse_tex)

add_order(ROOT/"res/field/area_data/area_data.order","area_data_077")
add_order(ROOT/"res/field/maps/texture_sets/map_texture_sets.order","map_texture_set_076")
add_meson_entry(ROOT/"res/field/area_data/meson.build","area_data_076.json",["area_data_077.json"])
add_meson_entry(ROOT/"res/field/maps/texture_sets/meson.build","map_texture_set_075.nsbtx",["map_texture_set_076.nsbtx"])

headers=ROOT/"include/data/map_headers.h"
s=headers.read_text()
pat=re.compile(r"(\[MAP_HEADER_VEILSTONE_CITY_GALACTIC_WAREHOUSE\]\s*=\s*\{.*?\n\s*\},)",re.S)
m=pat.search(s)
if not m:
    raise SystemExit("warehouse header not found")
block=m.group(1)
if ".areaDataArchiveID = area_data_031" not in block:
    raise SystemExit("warehouse header source area changed unexpectedly")
newblock=block.replace(".areaDataArchiveID = area_data_031",".areaDataArchiveID = area_data_077",1)
s=s[:m.start(1)]+newblock+s[m.end(1):]
headers.write_text(s)
print("Prepared isolated Galactic warehouse area_data_077 / texture_set_076.")
