#!/usr/bin/env python3
"""Find HGSS palette refinements that can be applied to Platinum-native art without changing pixels."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
PLAT=ROOT/'res/pokemon'
SPECIES=ROOT/'generated/species.txt'
VIEWS={'female_back.png':'female/back.png','male_back.png':'male/back.png','female_front.png':'female/front.png','male_front.png':'male/front.png'}

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument('--donor-root',required=True,type=Path)
    p.add_argument('--report',required=True,type=Path)
    p.add_argument('--manifest',required=True,type=Path)
    return p.parse_args()

def read_pal(path):
    lines=[x.strip() for x in path.read_text().splitlines() if x.strip()]
    n=int(lines[2]); return [tuple(map(int,x.split())) for x in lines[3:3+n]]

def embedded(path):
    with Image.open(path) as im:
        pal=im.getpalette()
        return [tuple(pal[i:i+3]) for i in range(0,48,3)]

def indices(path):
    with Image.open(path) as im:
        return list(im.getdata())

def dist(a,b):
    return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))

def main():
    a=parse_args(); rows=[]
    species_list=[x.strip() for x in SPECIES.read_text().splitlines() if x.strip()]
    for sid,species in enumerate(species_list):
        if species in {'SPECIES_NONE','SPECIES_EGG','SPECIES_BAD_EGG'}: continue
        base=PLAT/species.removeprefix('SPECIES_').lower()
        if not (base/'normal.pal').exists(): continue
        donor_dir=a.donor_root/f'{sid:04}'
        donor_pals=[]; identical_views=0; compared=0; art_diff=False
        for view,donor_rel in VIEWS.items():
            pp=base/view; hp=donor_dir/donor_rel
            if not pp.exists() or not hp.exists(): continue
            compared+=1
            if indices(pp)!=indices(hp):
                art_diff=True; break
            identical_views+=1; donor_pals.append(embedded(hp))
        if art_diff or compared==0: continue
        if any(p!=donor_pals[0] for p in donor_pals[1:]): continue
        target=read_pal(base/'normal.pal')
        donor=donor_pals[0]
        if target[:16]==donor[:16]: continue
        used=set()
        for view in VIEWS:
            pp=base/view
            if pp.exists(): used.update(i for i in indices(pp) if i!=0)
        used=sorted(i for i in used if i<16)
        changed=[i for i in used if target[i]!=donor[i]]
        if not changed: continue
        mean=sum(dist(target[i],donor[i]) for i in changed)/len(changed)
        maximum=max(dist(target[i],donor[i]) for i in changed)
        rows.append({'species_id':sid,'species':species,'compared_views':compared,'changed_used_indices':changed,'mean_rgb_distance':round(mean,2),'max_rgb_distance':round(maximum,2),'platinum_palette':[list(c) for c in target[:16]],'hgss_palette':[list(c) for c in donor[:16]]})
    rows.sort(key=lambda r:(-r['mean_rgb_distance'],r['species_id']))
    data={'schema_version':1,'policy':'Palette-only candidates: all compared sprite index maps are identical between Platinum and HGSS; no sprite pixels are changed.','summary':{'candidate_species':len(rows)},'results':rows}
    a.manifest.parent.mkdir(parents=True,exist_ok=True); a.manifest.write_text(json.dumps(data,indent=2)+'\n')
    lines=['# Platinum-Native HGSS Palette Reference Audit','',
           'Candidates below retain Platinum pixel art and animation exactly. HGSS contributes only later official normal-color palette values.','',
           f'- Candidate species: **{len(rows)}**','',
           '## Highest-impact candidates','']
    for r in rows[:60]:
        lines.append(f"- {r['species']}: mean RGB distance {r['mean_rgb_distance']}, max {r['max_rgb_distance']}, changed used indices {r['changed_used_indices']}")
    a.report.write_text('\n'.join(lines)+'\n')
    print(f'Found {len(rows)} palette-only native-art candidates.')

if __name__=='__main__': main()