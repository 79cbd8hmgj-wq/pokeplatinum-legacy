#!/usr/bin/env python3
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
REPORT=ROOT/"docs/visual_overhaul/G4C_DISTORTION_GRADE_REPORT.md"
TARGETS={"criff","criffP2","s_land","s_land2","s_land3","s_land4","s_land_att","s_land_jump_pl","s_landp","tree_sbt01"}

def validate(label):
    before=ROOT/f"docs/visual_overhaul/review/g4c_{label}_before"
    after=ROOT/f"docs/visual_overhaul/review/g4c_{label}_after"
    bp={p.name:p for p in before.glob("*.png")}
    ap={p.name:p for p in after.glob("*.png")}
    if bp.keys()!=ap.keys(): raise SystemExit(f"{label}: texture names changed")
    dims=[]; indices=[]; visual=[]
    for name in sorted(bp):
        with Image.open(bp[name]) as a, Image.open(ap[name]) as b:
            if a.size!=b.size:
                dims.append(name); continue
            if a.mode=="P" and b.mode=="P" and list(a.getdata())!=list(b.getdata()):
                indices.append(name)
            if a.convert("RGBA").tobytes()!=b.convert("RGBA").tobytes():
                visual.append(Path(name).stem)
    bpal={p.stem:p.read_text() for p in before.glob("*.pal")}
    apal={p.stem:p.read_text() for p in after.glob("*.pal")}
    if bpal.keys()!=apal.keys(): raise SystemExit(f"{label}: palette names changed")
    changed=sorted(k for k in bpal if bpal[k]!=apal[k])
    unexpected=sorted(set(changed)-TARGETS)
    if dims or indices or unexpected:
        raise SystemExit(f"{label}: dims={dims} indices={indices} unexpected={unexpected}")
    return len(bp),changed,visual

mc,mp,mv=validate("map")
pc,pp,pv=validate("props")
if not mp or not pp:
    raise SystemExit("expected both Distortion World banks to receive palette changes")

lines=[
"# G4C — Distortion World Palette Grade",
"",
"Status: source-applied; runtime inspection pending.",
"",
"Distortion World retains its native texture geometry and indexed texel maps while its harsh full-saturation blue/magenta accents are refined into a deeper indigo-violet presentation.",
"",
f"- Map textures validated: **{mc}**",
f"- Prop textures validated: **{pc}**",
f"- Map palettes changed: **{len(mp)}**",
f"- Prop palettes changed: **{len(pp)}**",
f"- Map rendered textures affected: **{len(mv)}**",
f"- Prop rendered textures affected: **{len(pv)}**",
"- Texture dimensions changed: **0**",
"- Indexed texel maps changed: **0**",
"",
"## Preserved",
"",
"- Distortion World map geometry, gravity mechanics, collision and scripts",
"- native red/black/blue visual identity",
"- water/fog texture families not targeted by the grade",
"- all resource names and texture indexing",
]
REPORT.write_text("\n".join(lines)+"\n")
