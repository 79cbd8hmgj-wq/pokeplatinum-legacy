#!/usr/bin/env python3
import json, re, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

def readj(path):
    return json.loads((ROOT/path).read_text())
def writej(path,data):
    p=ROOT/path; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,indent=4)+"\n")
def clamp(v): return max(0,min(31,v))

# G4D Spear Pillar: dedicated cool summit lighting derived from set 008.
spear=readj("res/field/lighting/lighting_set_008.json")
for k in spear:
    if 9000 <= k["endTime"] <= 30600:
        k["lights"][0]["color"]["blue"]=clamp(k["lights"][0]["color"]["blue"]+1)
        k["diffuseColor"]["red"]=clamp(k["diffuseColor"]["red"]-1)
        k["diffuseColor"]["blue"]=clamp(k["diffuseColor"]["blue"]+1)
        k["ambientColor"]["blue"]=clamp(k["ambientColor"]["blue"]+1)
        k["specularColor"]["blue"]=clamp(k["specularColor"]["blue"]+1)
writej("res/field/lighting/lighting_set_012.json",spear)

# G4E lakes: clean blue-green daylight derived from set 000.
lakes=readj("res/field/lighting/lighting_set_000.json")
for k in lakes:
    if 9000 <= k["endTime"] <= 30600:
        k["lights"][0]["color"]["green"]=clamp(k["lights"][0]["color"]["green"]+1)
        k["lights"][0]["color"]["blue"]=clamp(k["lights"][0]["color"]["blue"]+1)
        for field in ("diffuseColor","ambientColor"):
            k[field]["green"]=clamp(k[field]["green"]+1)
            k[field]["blue"]=clamp(k[field]["blue"]+1)
        k["specularColor"]["blue"]=clamp(k["specularColor"]["blue"]+1)
writej("res/field/lighting/lighting_set_013.json",lakes)

# G4F Turnback Cave: darker, cooler dedicated cave lighting derived from set 001.
turn=readj("res/field/lighting/lighting_set_001.json")
for k in turn:
    k["lights"][0]["color"]["red"]=clamp(k["lights"][0]["color"]["red"]-3)
    k["lights"][0]["color"]["green"]=clamp(k["lights"][0]["color"]["green"]-3)
    k["diffuseColor"]["red"]=clamp(k["diffuseColor"]["red"]-2)
    k["diffuseColor"]["green"]=clamp(k["diffuseColor"]["green"]-2)
    k["ambientColor"]["red"]=clamp(k["ambientColor"]["red"]-3)
    k["ambientColor"]["green"]=clamp(k["ambientColor"]["green"]-2)
    k["specularColor"]["red"]=clamp(k["specularColor"]["red"]-3)
    k["specularColor"]["green"]=clamp(k["specularColor"]["green"]-2)
    k["specularColor"]["blue"]=clamp(k["specularColor"]["blue"]+1)
    k["emissionColor"]["red"]=clamp(k["emissionColor"]["red"]-3)
    k["emissionColor"]["green"]=clamp(k["emissionColor"]["green"]-3)
    k["emissionColor"]["blue"]=clamp(k["emissionColor"]["blue"]-1)
writej("res/field/lighting/lighting_set_014.json",turn)

# Register lighting sets.
order=ROOT/"res/field/lighting/lighting_sets.order"
lines=[x for x in order.read_text().splitlines() if x]
for x in ("lighting_set_012","lighting_set_013","lighting_set_014"):
    if x not in lines: lines.append(x)
order.write_text("\n".join(lines)+"\n")
meson=ROOT/"res/field/lighting/meson.build"
s=meson.read_text()
if "'lighting_set_012.json'" not in s:
    s=s.replace("    'lighting_set_011.json'),","    'lighting_set_011.json',\n    'lighting_set_012.json',\n    'lighting_set_013.json',\n    'lighting_set_014.json'),")
meson.write_text(s)

# Point coherent Spear and lake area families at their new lighting.
a60=readj("res/field/area_data/area_data_060.json"); a60["lightingSet"]="lighting_set_012"; writej("res/field/area_data/area_data_060.json",a60)
a62=readj("res/field/area_data/area_data_062.json"); a62["lightingSet"]="lighting_set_013"; writej("res/field/area_data/area_data_062.json",a62)

# Turnback shares area 056 with Solaceon Ruins/Celestic Cave, so isolate it.
a76=readj("res/field/area_data/area_data_056.json")
a76["mapTextureSet"]="map_texture_set_075"
a76["lightingSet"]="lighting_set_014"
writej("res/field/area_data/area_data_076.json",a76)
shutil.copyfile(ROOT/"res/field/maps/texture_sets/map_texture_set_055.nsbtx",ROOT/"res/field/maps/texture_sets/map_texture_set_075.nsbtx")

area_order=ROOT/"res/field/area_data/area_data.order"
lines=[x for x in area_order.read_text().splitlines() if x]
if "area_data_076" not in lines: lines.append("area_data_076")
area_order.write_text("\n".join(lines)+"\n")
area_meson=ROOT/"res/field/area_data/meson.build"
s=area_meson.read_text()
if "'area_data_076.json'" not in s:
    s=s.replace("    'area_data_075.json'),","    'area_data_075.json',\n    'area_data_076.json'),")
area_meson.write_text(s)

tex_order=ROOT/"res/field/maps/texture_sets/map_texture_sets.order"
lines=[x for x in tex_order.read_text().splitlines() if x]
if "map_texture_set_075" not in lines: lines.append("map_texture_set_075")
tex_order.write_text("\n".join(lines)+"\n")
tex_meson=ROOT/"res/field/maps/texture_sets/meson.build"
s=tex_meson.read_text()
if "'map_texture_set_075.nsbtx'" not in s:
    s=s.replace("    'map_texture_set_074.nsbtx'\n))","    'map_texture_set_074.nsbtx',\n    'map_texture_set_075.nsbtx'\n))")
tex_meson.write_text(s)

# Redirect only Turnback Cave headers; leave Solaceon/Celestic users of area 056 alone.
headers=ROOT/"include/data/map_headers.h"
s=headers.read_text()
pat=re.compile(r"(\[MAP_HEADER_TURNBACK_CAVE[A-Z0-9_]*\]\s*=\s*\{.*?\n\s*\},)",re.S)
count=0
def repl(m):
    global count
    block=m.group(1)
    if ".areaDataArchiveID = area_data_056" in block:
        count+=1
        return block.replace(".areaDataArchiveID = area_data_056",".areaDataArchiveID = area_data_076",1)
    return block
s=pat.sub(repl,s)
if count < 20:
    raise SystemExit(f"expected >=20 Turnback headers, updated {count}")
headers.write_text(s)

doc=ROOT/"docs/visual_overhaul/G4D_G4F_SHOWCASE_ENVIRONMENTS.md"
doc.write_text("""# G4D–G4F — Showcase Environment Passes

Status: source-applied; runtime inspection pending.

## G4D — Spear Pillar

Spear Pillar, its distorted variant, Hall of Origin, and the Dialga/Palkia summit
rooms retain Platinum's geometry, collision, camera, weather, props, and ancient
stone identity. The area family now uses dedicated lighting_set_012, derived
from set 008 with a small cool high-altitude daylight lift.

## G4E — Sinnoh lakes

Lake Verity, Lake Valor, and Sendoff Spring use dedicated lighting_set_013,
derived from set 000. Daylight receives a restrained green-blue lift that
strengthens water/foliage atmosphere without replacing shore geometry or the
native warm evening transition.

## G4F — Turnback Cave

Turnback Cave previously shared area_data_056 with Solaceon Ruins and Celestic
Town Cave. G4 isolates Turnback into area_data_076 with a cloned texture slot
(map_texture_set_075) and dedicated lighting_set_014. Only Turnback Cave headers
are redirected.

Turnback lighting is darker and slightly cooler than the shared cave baseline.
Its texture bank is intentionally left pixel/palette-identical for now because
the dump contains bright green values likely used as key/transparency colors.
Changing those without material-level runtime evidence would be unsafe.

Across all three passes, map matrices, collision, scripts, encounters, camera
logic, weather, event progression, room randomization, and legendary logic are
unchanged.
""")
print(f"Prepared G4D-G4F structural/lighting pass; redirected {count} Turnback headers.")
