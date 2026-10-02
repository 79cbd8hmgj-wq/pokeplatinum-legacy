#!/usr/bin/env python3
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
BEFORE=ROOT/"docs/visual_overhaul/review/g4b_snow_before"
AFTER=ROOT/"docs/visual_overhaul/review/g4b_snow_after"
REPORT=ROOT/"docs/visual_overhaul/G4B_SNOW_ENVIRONMENT.md"

TARGETS={
    "beachp","blueglayp","ckado","enccriff","hage","lgreen","lgreenp",
    "nhana","nsandp","rhana","sandset","shana",
}

before_pngs={p.name:p for p in BEFORE.glob("*.png")}
after_pngs={p.name:p for p in AFTER.glob("*.png")}
if before_pngs.keys()!=after_pngs.keys():
    raise SystemExit("texture filename set changed")

dim=[]
indices=[]
visual=[]
for name in sorted(before_pngs):
    with Image.open(before_pngs[name]) as a, Image.open(after_pngs[name]) as b:
        if a.size!=b.size:
            dim.append(name)
            continue
        if a.mode=="P" and b.mode=="P" and list(a.getdata())!=list(b.getdata()):
            indices.append(name)
        if a.convert("RGBA").tobytes()!=b.convert("RGBA").tobytes():
            visual.append(Path(name).stem)

before_p={p.stem:p.read_text() for p in BEFORE.glob("*.pal")}
after_p={p.stem:p.read_text() for p in AFTER.glob("*.pal")}
if before_p.keys()!=after_p.keys():
    raise SystemExit("palette filename set changed")
changed=sorted(k for k in before_p if before_p[k]!=after_p[k])
unexpected=sorted(set(changed)-TARGETS)
if dim or indices or unexpected or len(changed)<6:
    raise SystemExit(f"validation failed dim={dim} indices={indices} unexpected={unexpected} changed={changed}")

lines=[
"# G4B — Snowpoint / Route 217 Environment",
"",
"Status: source-applied; runtime inspection pending.",
"",
"Platinum's shared Snowpoint/Route 217 terrain bank was conservatively graded to reduce the fluorescent green fringe that remains visible around snow-covered ground and foliage.",
"",
f"- Texture files validated: **{len(before_pngs)}**",
f"- Dimensions changed: **{len(dim)}**",
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
"- snow/ice whites and blue shading",
"- tree/trunk palettes",
"- rock, bridge, water, building, and prop textures",
"- map geometry and collision",
"- Blizzard/Snowpoint weather behavior",
"",
"The adjustment is deliberately smaller than the Eterna Forest grade: snow remains the dominant visual surface while exposed vegetation is less neon.",
]
REPORT.write_text("\n".join(lines)+"\n")
print(f"Validated {len(before_pngs)} textures; {len(changed)} palettes changed.")
