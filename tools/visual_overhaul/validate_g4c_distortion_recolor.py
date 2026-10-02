#!/usr/bin/env python3
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
BEFORE=ROOT/"docs/visual_overhaul/review/g4c_before"
AFTER=ROOT/"docs/visual_overhaul/review/g4c_after"
REPORT=ROOT/"docs/visual_overhaul/G4C_DISTORTION_WORLD.md"
TARGETS={"criff","criffP2","s_land","s_land2","s_land3","s_land_att","s_land_jump_pl","s_landp","tree_sbt01"}

bp={p.name:p for p in BEFORE.glob("*.png")}
ap={p.name:p for p in AFTER.glob("*.png")}
if bp.keys()!=ap.keys():
    raise SystemExit("texture filename set changed")

dims=[]
indices=[]
visual=[]
for name in sorted(bp):
    with Image.open(bp[name]) as a, Image.open(ap[name]) as b:
        if a.size!=b.size:
            dims.append(name)
            continue
        if a.mode=="P" and b.mode=="P" and list(a.getdata())!=list(b.getdata()):
            indices.append(name)
        if a.convert("RGBA").tobytes()!=b.convert("RGBA").tobytes():
            visual.append(Path(name).stem)

bpal={p.stem:p.read_text() for p in BEFORE.glob("*.pal")}
apal={p.stem:p.read_text() for p in AFTER.glob("*.pal")}
if bpal.keys()!=apal.keys():
    raise SystemExit("palette filename set changed")
changed=sorted(k for k in bpal if bpal[k]!=apal[k])
unexpected=sorted(set(changed)-TARGETS)
if dims or indices or unexpected or len(changed)<6:
    raise SystemExit(f"validation failed dims={dims} indices={indices} unexpected={unexpected} changed={changed}")

lines=[
"# G4C — Distortion World Environment",
"",
"Status: source-applied; runtime inspection pending.",
"",
"The Distortion World keeps Platinum's native geometry, surreal materials, and static purple lighting identity. The environment pass only tempers the most saturated electric-blue and hot-magenta accents so the dark stone and red-violet terrain retain more depth.",
"",
f"- Texture files validated: **{len(bp)}**",
f"- Dimensions changed: **{len(dims)}**",
f"- Indexed texel maps changed: **{len(indices)}**",
f"- Palettes changed: **{len(changed)}**",
f"- Rendered textures affected: **{len(visual)}**",
"",
"## Changed palettes",
"",
]
lines += [f"- {x}" for x in changed]
lines += [
"",
"## Preserved",
"",
"- all Distortion World map geometry and collision",
"- texture dimensions, texel indices, and transparency",
"- lake/water palettes",
"- the native red-violet stone palette family",
"- lighting_set_009 and its deliberately time-invariant surreal lighting",
"- scripts, camera behavior, gravity/map logic, and Giratina progression",
"",
"This is a polish pass, not a redesign: the Distortion World remains immediately recognizable as Platinum's Distortion World.",
]
REPORT.write_text("\n".join(lines)+"\n")
print(f"Validated {len(bp)} textures; {len(changed)} palettes changed.")
