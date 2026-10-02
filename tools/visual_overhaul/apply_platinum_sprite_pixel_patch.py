#!/usr/bin/env python3
"""Apply small, auditable indexed-pixel edits to Platinum battle sprites."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
POKEMON=ROOT/"res"/"pokemon"

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument("manifest",type=Path)
    p.add_argument("--dry-run",action="store_true")
    return p.parse_args()

def main():
    a=parse_args()
    data=json.loads(a.manifest.read_text())
    edits=data.get("edits",[])
    touched=set()

    for edit in edits:
        species=edit["species"]
        view=edit["view"]
        frame=int(edit["frame"])
        x=int(edit["x"]); y=int(edit["y"])
        expected=int(edit["from"]); replacement=int(edit["to"])

        if frame not in (0,1): raise SystemExit(f"bad frame: {frame}")
        if not (0<=x<80 and 0<=y<80): raise SystemExit(f"bad coordinate: {x},{y}")
        if not (0<=expected<=15 and 0<=replacement<=15):
            raise SystemExit("palette indices must remain 0..15")

        path=POKEMON/species.removeprefix("SPECIES_").lower()/view
        with Image.open(path) as im:
            im.load()
            if im.mode!="P" or im.size!=(160,80):
                raise SystemExit(f"{path}: unexpected sprite contract")
            px=im.load()
            gx=x+frame*80
            current=int(px[gx,y])
            if current!=expected:
                raise SystemExit(
                    f"{path} frame {frame} ({x},{y}): expected {expected}, found {current}"
                )
            if not a.dry_run:
                px[gx,y]=replacement
                im.save(path)
        touched.add(str(path))
        print(f"{species} {view} f{frame} ({x},{y}): {expected}->{replacement}")

    print(f"{'Would touch' if a.dry_run else 'Touched'} {len(touched)} files with {len(edits)} indexed-pixel edits.")

if __name__=="__main__":
    main()
