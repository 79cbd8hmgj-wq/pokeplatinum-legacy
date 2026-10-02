#!/usr/bin/env python3
"""Audit Platinum-native Pokemon battle sprites for cleanup opportunities."""
from __future__ import annotations
import argparse, json
from dataclasses import asdict, dataclass
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
POKEMON_ROOT=ROOT/"res"/"pokemon"
SPECIES_LIST=ROOT/"generated"/"species.txt"
VIEWS=("female_back.png","male_back.png","female_front.png","male_front.png")
FRAME_W=80
FRAME_H=80

@dataclass
class Frame:
    frame:int
    bbox:tuple[int,int,int,int]|None
    opaque:int
    edge_touch:bool
    isolated:int

@dataclass
class Sprite:
    species:str
    view:str
    mode:str
    size:tuple[int,int]
    used_indices:list[int]
    rare_indices:list[int]
    frames:list[Frame]
    center_dx:float|None
    center_dy:float|None
    flags:list[str]

def args():
    p=argparse.ArgumentParser()
    p.add_argument("--report",required=True,type=Path)
    p.add_argument("--manifest",required=True,type=Path)
    return p.parse_args()

def frame_metrics(im, n):
    crop=im.crop((n*FRAME_W,0,(n+1)*FRAME_W,FRAME_H))
    px=list(crop.getdata())
    pts={(i%FRAME_W,i//FRAME_W) for i,v in enumerate(px) if v!=0}
    if not pts:
        return Frame(n,None,0,False,0)
    xs=[x for x,_ in pts]; ys=[y for _,y in pts]
    box=(min(xs),min(ys),max(xs)+1,max(ys)+1)
    iso=0
    for x,y in pts:
        if not any((nx,ny)!=(x,y) and (nx,ny) in pts
                   for ny in range(max(0,y-1),min(FRAME_H,y+2))
                   for nx in range(max(0,x-1),min(FRAME_W,x+2))):
            iso+=1
    l,t,r,b=box
    return Frame(n,box,len(pts),l==0 or t==0 or r==FRAME_W or b==FRAME_H,iso)

def ctr(box):
    if box is None: return None
    l,t,r,b=box
    return ((l+r)/2,(t+b)/2)

def audit_one(species,view,path):
    with Image.open(path) as im:
        im.load()
        counts={}
        for v in im.getdata(): counts[v]=counts.get(v,0)+1
        used=sorted(i for i in counts if i)
        rare=sorted(i for i in used if counts[i]<=2)
        frames=[frame_metrics(im,0),frame_metrics(im,1)]
        flags=[]
        if im.mode!="P": flags.append(f"non-indexed mode {im.mode}")
        if im.size!=(160,80): flags.append(f"unexpected size {im.size[0]}x{im.size[1]}")
        if any(i>15 for i in used): flags.append("uses palette index above 15")
        if any(f.edge_touch for f in frames): flags.append("frame-edge contact")
        if any(f.isolated for f in frames): flags.append("isolated opaque pixels")
        if rare: flags.append("rare palette indices")
        c0,c1=ctr(frames[0].bbox),ctr(frames[1].bbox)
        dx=dy=None
        if c0 and c1:
            dx=c1[0]-c0[0]; dy=c1[1]-c0[1]
            if abs(dx)>8 or abs(dy)>8: flags.append("large frame-to-frame center shift")
        return Sprite(species,view,im.mode,im.size,used,rare,frames,dx,dy,flags)

def main():
    a=args()
    results=[]; missing=[]
    for species in [x.strip() for x in SPECIES_LIST.read_text().splitlines() if x.strip()]:
        if species in {"SPECIES_EGG","SPECIES_BAD_EGG"}: continue
        base=POKEMON_ROOT/species.removeprefix("SPECIES_").lower()
        for view in VIEWS:
            path=base/view
            if path.exists(): results.append(audit_one(species,view,path))
            else: missing.append(f"{species}:{view}")
    edge=[r for r in results if any(f.edge_touch for f in r.frames)]
    isolated=[r for r in results if any(f.isolated for f in r.frames)]
    motion=[r for r in results if r.center_dx is not None and (abs(r.center_dx)>8 or abs(r.center_dy or 0)>8)]
    rare=[r for r in results if r.rare_indices]
    flagged=[r for r in results if r.flags]
    priority=sorted({r.species for r in edge+isolated+motion})
    data={"schema_version":1,"policy":"Platinum-native battle sprites are canonical; findings are review signals, not automatic edits.","summary":{"sprite_files_audited":len(results),"missing_paths":len(missing),"flagged_files":len(flagged),"edge_touch_files":len(edge),"isolated_pixel_files":len(isolated),"rare_index_files":len(rare),"large_motion_files":len(motion),"priority_species":len(priority)},"priority_species":priority,"results":[asdict(r) for r in results],"missing_paths":missing}
    a.manifest.parent.mkdir(parents=True,exist_ok=True)
    a.manifest.write_text(json.dumps(data,indent=2)+"\n")
    lines=["# Platinum Native Battle Sprite Audit","","Platinum battle sprites are the canonical G3C source. Findings below are review signals, not automatic errors.","","## Summary","",f"- Sprite files audited: **{len(results)}**",f"- Missing paths: **{len(missing)}**",f"- Flagged files: **{len(flagged)}**",f"- Frame-edge contact files: **{len(edge)}**",f"- Isolated-pixel files: **{len(isolated)}**",f"- Rare-index files: **{len(rare)}**",f"- Large frame-motion files: **{len(motion)}**",f"- Priority species: **{len(priority)}**","","## Priority review species",""]
    lines += [f"- {s}" for s in priority] or ["- None"]
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text("\n".join(lines)+"\n")
    print(f"Audited {len(results)} native sprite files; {len(priority)} species prioritized.")

if __name__=="__main__": main()
