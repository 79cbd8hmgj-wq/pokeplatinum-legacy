#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[2]
src=Image.open(ROOT/"res/pokemon/pikachu/male_front.png").convert("RGBA")
out=ROOT/"docs/visual_overhaul/review"
out.mkdir(parents=True,exist_ok=True)
for frame in (0,1):
    crop=src.crop((frame*80,0,(frame+1)*80,80))
    bbox=crop.getbbox()
    if bbox is None: continue
    l,t,r,b=bbox
    pad=3
    l=max(0,l-pad); t=max(0,t-pad); r=min(80,r+pad); b=min(80,b+pad)
    crop=crop.crop((l,t,r,b))
    scale=12
    big=crop.resize((crop.width*scale,crop.height*scale),Image.Resampling.NEAREST)
    canvas=Image.new("RGBA",(big.width+70,big.height+50),(255,255,255,255))
    canvas.paste(big,(60,35))
    d=ImageDraw.Draw(canvas)
    for x in range(crop.width+1):
        gx=60+x*scale
        d.line((gx,35,gx,35+big.height),fill=(0,0,0,80),width=1)
    for y in range(crop.height+1):
        gy=35+y*scale
        d.line((60,gy,60+big.width,gy),fill=(0,0,0,80),width=1)
    for x in range(crop.width):
        if (l+x)%5==0:
            d.text((60+x*scale,5),str(l+x),fill=(0,0,0,255))
    for y in range(crop.height):
        if (t+y)%5==0:
            d.text((5,35+y*scale),str(t+y),fill=(0,0,0,255))
    d.text((5,5),f"frame {frame} bbox {bbox}",fill=(0,0,0,255))
    canvas.convert("RGB").save(out/f"pikachu_male_front_frame{frame}_grid.png")
