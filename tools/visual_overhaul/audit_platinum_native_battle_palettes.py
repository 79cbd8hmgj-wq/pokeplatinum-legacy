#!/usr/bin/env python3
"""Audit Platinum-native battle sprite palettes for readability/polish candidates."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
POKEMON=ROOT/"res"/"pokemon"
SPECIES=ROOT/"generated"/"species.txt"
VIEWS=("female_back.png","male_back.png","female_front.png","male_front.png")

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument("--report",required=True,type=Path)
    p.add_argument("--manifest",required=True,type=Path)
    return p.parse_args()

def read_pal(path):
    lines=[x.strip() for x in path.read_text().splitlines() if x.strip()]
    if len(lines)<4 or lines[0]!="JASC-PAL": raise ValueError(str(path))
    n=int(lines[2])
    return [tuple(map(int,x.split())) for x in lines[3:3+n]]

def lum(c):
    r,g,b=c
    return 0.2126*r+0.7152*g+0.0722*b

def dist(a,b):
    return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))

def used_indices(base):
    used=set()
    for view in VIEWS:
        p=base/view
        if not p.exists(): continue
        with Image.open(p) as im:
            used.update(int(x) for x in im.getdata() if int(x)!=0)
    return sorted(used)

def main():
    a=parse_args()
    rows=[]
    for species in [x.strip() for x in SPECIES.read_text().splitlines() if x.strip()]:
        if species in {"SPECIES_NONE","SPECIES_EGG","SPECIES_BAD_EGG"}: continue
        base=POKEMON/species.removeprefix("SPECIES_").lower()
        np=base/"normal.pal"; sp=base/"shiny.pal"
        if not np.exists() or not sp.exists(): continue
        normal=read_pal(np); shiny=read_pal(sp); used=used_indices(base)
        used=[i for i in used if i < len(normal)]
        if not used: continue

        dup=[]
        near=[]
        for pos,i in enumerate(used):
            for j in used[pos+1:]:
                d=dist(normal[i],normal[j])
                if d==0: dup.append([i,j])
                elif d<=18: near.append({"indices":[i,j],"distance":round(d,2)})

        lums=[lum(normal[i]) for i in used]
        span=max(lums)-min(lums) if lums else 0
        shiny_same=sum(1 for i in used if i < len(shiny) and normal[i]==shiny[i])

        flags=[]
        if dup: flags.append("duplicate-used-colors")
        if len(near)>=3: flags.append("crowded-color-ramp")
        if span<70: flags.append("low-luminance-span")
        if shiny_same==len(used): flags.append("shiny-identical-on-used-indices")

        if flags:
            rows.append({
                "species":species,
                "used_indices":used,
                "duplicate_pairs":dup,
                "near_pairs":near,
                "luminance_span":round(span,2),
                "shiny_same_used_indices":shiny_same,
                "flags":flags,
            })

    duplicates=[r for r in rows if "duplicate-used-colors" in r["flags"]]
    crowded=[r for r in rows if "crowded-color-ramp" in r["flags"]]
    low=[r for r in rows if "low-luminance-span" in r["flags"]]
    identical=[r for r in rows if "shiny-identical-on-used-indices" in r["flags"]]

    data={"schema_version":1,"policy":"Audit only; no palette is modified automatically.",
          "summary":{"flagged_species":len(rows),"duplicate_used_color_species":len(duplicates),
                     "crowded_ramp_species":len(crowded),"low_luminance_span_species":len(low),
                     "shiny_identical_species":len(identical)},
          "results":rows}
    a.manifest.parent.mkdir(parents=True,exist_ok=True)
    a.manifest.write_text(json.dumps(data,indent=2)+"\n")

    lines=["# Platinum Native Battle Sprite Palette Audit","",
           "Audit-only G3C pass. Platinum palettes remain canonical and unchanged.","",
           "## Summary","",
           f"- Flagged species: **{len(rows)}**",
           f"- Duplicate used-color species: **{len(duplicates)}**",
           f"- Crowded color-ramp species: **{len(crowded)}**",
           f"- Low luminance-span species: **{len(low)}**",
           f"- Shiny identical on used indices: **{len(identical)}**","",
           "## Exact duplicate used-color candidates",""]
    lines += [f"- {r['species']}: {r['duplicate_pairs']}" for r in duplicates] or ["- None"]
    lines += ["","## Crowded color-ramp candidates",""]
    lines += [f"- {r['species']}: {len(r['near_pairs'])} near-color pairs" for r in crowded] or ["- None"]
    lines += ["","## Low luminance-span candidates",""]
    lines += [f"- {r['species']}: span {r['luminance_span']}" for r in low] or ["- None"]
    lines += ["","## Shiny-identical candidates",""]
    lines += [f"- {r['species']}" for r in identical] or ["- None"]
    a.report.write_text("\n".join(lines)+"\n")
    print(f"Flagged {len(rows)} species for palette review.")

if __name__=="__main__": main()
