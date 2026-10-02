#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"docs/visual_overhaul/review/g4a_eterna_dump"
OUT=ROOT/"docs/visual_overhaul/review"

def sheet_for(folder: Path, out: Path):
    files=sorted(folder.glob("*.png"))
    thumbs=[]
    for p in files:
        im=Image.open(p).convert("RGBA")
        scale=max(1,min(6,192//max(im.width,im.height)))
        big=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)
        canvas=Image.new("RGBA",(max(210,big.width+12),big.height+36),(245,245,245,255))
        canvas.paste(big,((canvas.width-big.width)//2,28),big)
        d=ImageDraw.Draw(canvas)
        d.text((5,5),p.stem,fill=(0,0,0,255))
        thumbs.append(canvas)
    if not thumbs:
        return
    cols=4
    cellw=max(i.width for i in thumbs)
    rows=(len(thumbs)+cols-1)//cols
    rowh=max(i.height for i in thumbs)
    result=Image.new("RGB",(cols*cellw,rows*rowh),(230,230,230))
    for n,im in enumerate(thumbs):
        x=(n%cols)*cellw
        y=(n//cols)*rowh
        result.paste(im.convert("RGB"),(x,y))
    result.save(out)

sheet_for(SRC/"map",OUT/"g4a_eterna_map_textures.png")
sheet_for(SRC/"props",OUT/"g4a_eterna_prop_textures.png")
