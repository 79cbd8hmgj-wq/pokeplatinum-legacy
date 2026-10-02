#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
POKEMON=ROOT/"res"/"pokemon"
SPECIES=ROOT/"generated"/"species.txt"
VIEWS=("female_back.png","male_back.png","female_front.png","male_front.png")

def isolated_points(path):
    found=[]
    with Image.open(path) as im:
        im.load()
        for frame in (0,1):
            crop=im.crop((frame*80,0,(frame+1)*80,80))
            px=list(crop.getdata())
            pts={(i%80,i//80) for i,v in enumerate(px) if v!=0}
            for x,y in pts:
                neighbor=any((nx,ny)!=(x,y) and (nx,ny) in pts
                    for ny in range(max(0,y-1),min(80,y+2))
                    for nx in range(max(0,x-1),min(80,x+2)))
                if not neighbor:
                    found.append((frame,x,y,px[y*80+x]))
    return found

rows=[]
for species in [x.strip() for x in SPECIES.read_text().splitlines() if x.strip()]:
    if species in {"SPECIES_EGG","SPECIES_BAD_EGG","SPECIES_NONE"}:
        continue
    base=POKEMON/species.removeprefix("SPECIES_").lower()
    for view in VIEWS:
        p=base/view
        if p.exists():
            pts=isolated_points(p)
            if pts:
                rows.append((species,view,pts))

lines=["# Platinum Native Low-Risk Sprite Candidates","",
"Native Platinum battle-sprite files containing opaque pixels with no opaque 8-neighbor.",
"These are review candidates; no art is changed by this tool.","",
f"- Files: **{len(rows)}**",f"- Total isolated pixels: **{sum(len(p) for _,_,p in rows)}**","",
"## Candidates",""]
for species,view,pts in rows:
    detail=", ".join(f"frame {f} ({x},{y}) index {idx}" for f,x,y,idx in pts)
    lines.append(f"- {species} / {view}: {detail}")
(ROOT/"docs/visual_overhaul/PLATINUM_NATIVE_LOW_RISK_CANDIDATES.md").write_text("\n".join(lines)+"\n")
print(f"Wrote {len(rows)} candidate files.")
