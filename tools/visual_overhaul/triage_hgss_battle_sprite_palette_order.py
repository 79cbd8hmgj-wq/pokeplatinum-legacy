#!/usr/bin/env python3
"""Triage HGSS donor palette mismatches for index-order compatibility.

This does not change palettes or sprite pixels. It asks whether the donor's
non-transparent palette indices still appear to carry the same semantic color
ordering as Platinum even when the RGB values differ.
"""

from __future__ import annotations

import argparse
import json
import math
from functools import lru_cache
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PLATINUM = ROOT / "res" / "pokemon"
VIEW_TO_DONOR = {
    "female_back.png": "female/back.png",
    "male_back.png": "male/back.png",
    "female_front.png": "female/front.png",
    "male_front.png": "male/front.png",
}


def args() -> argparse.Namespace:
    p=argparse.ArgumentParser()
    p.add_argument("--donor-root",required=True,type=Path)
    p.add_argument("--palette-manifest",required=True,type=Path)
    p.add_argument("--report",required=True,type=Path)
    p.add_argument("--manifest",required=True,type=Path)
    return p.parse_args()


def parse_jasc(path:Path)->list[tuple[int,int,int]]:
    lines=[x.strip() for x in path.read_text().splitlines() if x.strip()]
    n=int(lines[2])
    return [tuple(map(int,x.split())) for x in lines[3:3+n]]


def png_palette(path:Path)->list[tuple[int,int,int]]:
    with Image.open(path) as im:
        p=im.getpalette()
        if p is None: raise ValueError(f"{path}: no palette")
        return [tuple(p[i:i+3]) for i in range(0,48,3)]


def used_indices(path:Path)->list[int]:
    with Image.open(path) as im:
        return sorted(set(im.getdata())-{0})


def cost(a:tuple[int,int,int],b:tuple[int,int,int])->int:
    return sum((x-y)*(x-y) for x,y in zip(a,b))


def optimal_assignment(donor:list[tuple[int,int,int]], target:list[tuple[int,int,int]], used:list[int])->tuple[int,dict[int,int]]:
    rows=tuple(used)
    targets=tuple(range(1,min(16,len(target))))
    @lru_cache(maxsize=None)
    def dp(pos:int,mask:int)->tuple[int,tuple[int,...]]:
        if pos==len(rows): return (0,())
        i=rows[pos]
        best=(10**18,())
        for j in targets:
            bit=1<<j
            if mask & bit: continue
            sub,tail=dp(pos+1,mask|bit)
            here=cost(donor[i],target[j])+sub
            if here<best[0]: best=(here,(j,)+tail)
        return best
    total,mapping_tuple=dp(0,0)
    return total,{i:j for i,j in zip(rows,mapping_tuple)}


def main()->None:
    a=args()
    src=json.loads(a.palette_manifest.read_text())
    mismatch=set(src["palette_mismatch_species"])
    entries=[]
    by_species={}

    for e in src["entries"]:
        if e["species"] not in mismatch or e["status"]!="palette-mismatch": continue
        species=e["species"]
        species_dir=species.removeprefix("SPECIES_").lower()
        donor=a.donor_root/e["donor_path"]
        dp=png_palette(donor)
        tp=parse_jasc(PLATINUM/species_dir/"normal.pal")
        used=used_indices(donor)
        identity=sum(cost(dp[i],tp[i]) for i in used)
        optimum,mapping=optimal_assignment(dp,tp,used)
        identity_mapping=all(mapping.get(i)==i for i in used)
        ratio=(identity/optimum) if optimum else (1.0 if identity==0 else math.inf)
        dists={str(i):round(math.sqrt(cost(dp[i],tp[i])),2) for i in used}
        entry={
            "species":species,"view":e["view"],"used_indices":used,
            "identity_cost":identity,"optimal_cost":optimum,
            "identity_to_optimal_ratio":round(ratio,4) if math.isfinite(ratio) else None,
            "optimal_mapping":{str(k):v for k,v in mapping.items()},
            "optimal_mapping_is_identity":identity_mapping,
            "same_index_rgb_distance":dists,
            "max_same_index_rgb_distance":max(dists.values()) if dists else 0,
        }
        entries.append(entry)
        by_species.setdefault(species,[]).append(entry)

    identity_species=sorted(s for s,v in by_species.items() if v and all(x["optimal_mapping_is_identity"] for x in v))
    reordered_species=sorted(s for s,v in by_species.items() if any(not x["optimal_mapping_is_identity"] for x in v))

    out={
      "schema_version":1,
      "interpretation":{
        "identity_order_candidate":"For every mismatched view, the globally minimum RGB assignment keeps each used donor index on the same Platinum index. This supports shared index semantics but is not runtime approval.",
        "reorder_suspected":"At least one view is better explained by a non-identity palette-index assignment; manual conversion/review remains required."
      },
      "summary":{
        "mismatch_species_input":len(mismatch),
        "views_checked":len(entries),
        "identity_order_candidate_species":len(identity_species),
        "reorder_suspected_species":len(reordered_species)
      },
      "identity_order_candidate_species":identity_species,
      "reorder_suspected_species":reordered_species,
      "entries":entries
    }
    a.manifest.parent.mkdir(parents=True,exist_ok=True)
    a.manifest.write_text(json.dumps(out,indent=2)+"\n")

    lines=[
      "# HGSS Battle Sprite Palette-Order Triage","",
      "This pass examines the 41 geometry-close species that failed exact RGB palette matching.",
      "It does **not** modify Platinum palettes and does **not** promote anything to runtime-safe by itself.","",
      "For each changed view, it solves a minimum-cost one-to-one assignment between the",
      "HGSS donor's used palette colors and Platinum's non-transparent palette indices.",
      "If the optimum is still the identity mapping, the evidence supports that HGSS and",
      "Platinum kept the same palette-index semantics and only changed the actual colors.","",
      "## Summary","",
      f"- Palette-mismatch species input: **{len(mismatch)}**",
      f"- Views checked: **{len(entries)}**",
      f"- Identity-order candidate species: **{len(identity_species)}**",
      f"- Reorder-suspected species: **{len(reordered_species)}**","",
      "## Identity-order candidates",""
    ]
    lines += [f"- {s}" for s in identity_species] or ["- None"]
    lines += ["","## Reorder-suspected species",""]
    lines += [f"- {s}" for s in reordered_species] or ["- None"]
    lines += ["","## Rule","",
      "Identity-order candidates may be tested later with Platinum's retained normal/shiny",
      "palettes because no index permutation is indicated. Reorder-suspected species remain",
      "on the explicit conversion path. Neither category bypasses runtime animation validation."
    ]
    a.report.write_text("\n".join(lines)+"\n")
    print(f"Checked {len(entries)} views: {len(identity_species)} identity-order candidates, {len(reordered_species)} reorder-suspected species.")


if __name__=="__main__":
    main()
