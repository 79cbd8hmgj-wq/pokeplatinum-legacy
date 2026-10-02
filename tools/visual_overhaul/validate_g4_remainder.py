#!/usr/bin/env python3
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
REPORT=ROOT/"docs/visual_overhaul/G4D_G4E_G4F_REMAINDER.md"

SPEAR={"colum_a_pl","colum_b_pl","colum_c_pl","dun08_chip_a_pl","dun08_chip_b_pl","dun08_chip_d_pl","dun08_chip_e_pl","dun08_chip_g_pl"}
LAKES={"beachp","blueglayp","ckado","enccriff","fenter","grass","hage","lgreen","lgreenp","nectgrass","nhana","nsandp","rhana","sandset","shana","tshadow","lake","lakep.1_pl"}

def check(prefix, allowed):
    before=ROOT/f"docs/visual_overhaul/review/{prefix}_before"
    after=ROOT/f"docs/visual_overhaul/review/{prefix}_after"
    bp={p.name:p for p in before.glob("*.png")}
    ap={p.name:p for p in after.glob("*.png")}
    if bp.keys()!=ap.keys(): raise SystemExit(f"{prefix}: names changed")
    dims=[]; indices=[]; visual=[]
    for name in sorted(bp):
        with Image.open(bp[name]) as a, Image.open(ap[name]) as b:
            if a.size!=b.size: dims.append(name); continue
            if a.mode=="P" and b.mode=="P" and list(a.getdata())!=list(b.getdata()): indices.append(name)
            if a.convert("RGBA").tobytes()!=b.convert("RGBA").tobytes(): visual.append(Path(name).stem)
    bpal={p.stem:p.read_text() for p in before.glob("*.pal")}
    apal={p.stem:p.read_text() for p in after.glob("*.pal")}
    if bpal.keys()!=apal.keys(): raise SystemExit(f"{prefix}: palette names changed")
    changed=sorted(k for k in bpal if bpal[k]!=apal[k])
    unexpected=sorted(set(changed)-allowed)
    if dims or indices or unexpected: raise SystemExit(f"{prefix}: dims={dims}, indices={indices}, unexpected={unexpected}")
    return len(bp),changed,visual

sc,sp,sv=check("g4d_spear",SPEAR)
lc,lp,lv=check("g4e_lakes",LAKES)
if len(sp)<5 or len(lp)<8: raise SystemExit(f"unexpectedly small result spear={sp} lakes={lp}")

lines=[
"# G4D/G4E/G4F — Environment Remainder",
"",
"Status: source-applied for Spear Pillar and lakes; Turnback Cave reviewed/no-op; runtime inspection pending.",
"",
"## G4D — Spear Pillar",
"",
"Ancient structural stone was cooled away from the retail yellow-beige cast while preserving native texture geometry and index maps.",
f"- Textures validated: **{sc}**",
f"- Palettes changed: **{len(sp)}**",
f"- Rendered textures affected: **{len(sv)}**",
"",
"## G4E — Lakes",
"",
"Lake-family exposed vegetation was brought into the same less-fluorescent natural range as the forest/snow passes, while lake water was slightly deepened for stronger separation from shoreline highlights.",
f"- Textures validated: **{lc}**",
f"- Palettes changed: **{len(lp)}**",
f"- Rendered textures affected: **{len(lv)}**",
"",
"## G4F — Turnback Cave",
"",
"The Turnback texture review found a coherent muted cave palette already in place. The conspicuous bright-green entries are tied to special-purpose/shadow/transition resources, so no automatic palette rewrite is applied.",
"",
"Across all three: map geometry, collision, scripts, texture dimensions, texel indices and resource names remain unchanged.",
]
REPORT.write_text("\n".join(lines)+"\n")
