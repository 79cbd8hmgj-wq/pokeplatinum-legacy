#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw
import argparse

p=argparse.ArgumentParser()
p.add_argument("source",type=Path)
p.add_argument("output",type=Path)
args=p.parse_args()

files=sorted(args.source.glob("*.png"))
thumbs=[]
for path in files:
    im=Image.open(path).convert("RGBA")
    scale=max(1,min(6,192//max(im.width,im.height)))
    big=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)
    canvas=Image.new("RGBA",(max(210,big.width+12),big.height+36),(245,245,245,255))
    canvas.paste(big,((canvas.width-big.width)//2,28),big)
    d=ImageDraw.Draw(canvas)
    d.text((5,5),path.stem,fill=(0,0,0,255))
    thumbs.append(canvas)
if not thumbs:
    raise SystemExit("no PNG textures found")
cols=4
cellw=max(i.width for i in thumbs)
rowh=max(i.height for i in thumbs)
rows=(len(thumbs)+cols-1)//cols
sheet=Image.new("RGB",(cols*cellw,rows*rowh),(230,230,230))
for n,im in enumerate(thumbs):
    sheet.paste(im.convert("RGB"),((n%cols)*cellw,(n//cols)*rowh))
args.output.parent.mkdir(parents=True,exist_ok=True)
sheet.save(args.output)
print(f"Wrote {len(files)} textures to {args.output}")
