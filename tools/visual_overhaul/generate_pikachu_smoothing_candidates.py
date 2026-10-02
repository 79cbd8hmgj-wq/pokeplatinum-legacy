#!/usr/bin/env python3
from collections import Counter
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"res/pokemon/pikachu/male_front.png"
OUT=ROOT/"docs/visual_overhaul/review/pikachu_native_smoothing_candidates.png"

im=Image.open(SRC)
palette=im.getpalette()
frames=[im.crop((0,0,80,80)),im.crop((80,0,160,80))]

def fill_notches(src):
    dst=src.copy(); p=src.load(); q=dst.load()
    for y in range(1,79):
        for x in range(1,79):
            if p[x,y]!=0: continue
            vals=[p[nx,ny] for ny in range(y-1,y+2) for nx in range(x-1,x+2)
                  if (nx,ny)!=(x,y) and p[nx,ny]!=0]
            if len(vals)>=5:
                q[x,y]=Counter(vals).most_common(1)[0][0]
    return dst

def remove_spikes(src):
    dst=src.copy(); p=src.load(); q=dst.load()
    for y in range(1,79):
        for x in range(1,79):
            if p[x,y]==0: continue
            occupied=sum(1 for ny in range(y-1,y+2) for nx in range(x-1,x+2)
                         if (nx,ny)!=(x,y) and p[nx,ny]!=0)
            if occupied<=1:
                q[x,y]=0
    return dst

def both(src):
    return remove_spikes(fill_notches(src))

variants=[("Original",frames[1]),("Fill notches",fill_notches(frames[1])),
          ("Remove spikes",remove_spikes(frames[1])),("Both",both(frames[1]))]

scale=7
panels=[]
for label,img in variants:
    rgba=img.convert("RGBA").resize((80*scale,80*scale),Image.Resampling.NEAREST)
    canvas=Image.new("RGBA",(80*scale,80*scale+28),(255,255,255,255))
    canvas.paste(rgba,(0,28))
    d=ImageDraw.Draw(canvas); d.text((6,6),label,fill=(0,0,0,255))
    panels.append(canvas)

sheet=Image.new("RGBA",(len(panels)*80*scale,80*scale+28),(255,255,255,255))
for i,panel in enumerate(panels): sheet.paste(panel,(i*80*scale,0))
OUT.parent.mkdir(parents=True,exist_ok=True)
sheet.convert("RGB").save(OUT)
