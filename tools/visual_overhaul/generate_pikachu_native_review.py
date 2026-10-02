#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
PLAT=ROOT/"res"/"pokemon"/"pikachu"
OUT=ROOT/"docs"/"visual_overhaul"/"review"
DONOR=Path(__import__("sys").argv[1])/"0025"

pairs=[
 ("male_front.png", DONOR/"male"/"front.png"),
 ("female_front.png", DONOR/"female"/"front.png"),
 ("male_back.png", DONOR/"male"/"back.png"),
 ("female_back.png", DONOR/"female"/"back.png"),
]
OUT.mkdir(parents=True,exist_ok=True)

for name, donor_path in pairs:
    p=Image.open(PLAT/name).convert("RGBA")
    h=Image.open(donor_path).convert("RGBA")
    diff=Image.new("RGBA",p.size,(0,0,0,0))
    dp=diff.load(); pp=p.load(); hp=h.load()
    for y in range(p.height):
        for x in range(p.width):
            if pp[x,y]!=hp[x,y]:
                dp[x,y]=(255,0,255,255)
            else:
                r,g,b,a=pp[x,y]
                dp[x,y]=(r//3,g//3,b//3,a)
    scale=4
    panels=[]
    for im,label in ((p,"Platinum"),(h,"HGSS"),(diff,"Diff")):
        big=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)
        canvas=Image.new("RGBA",(big.width,big.height+24),(255,255,255,255))
        canvas.paste(big,(0,24))
        d=ImageDraw.Draw(canvas)
        d.text((4,4),label,fill=(0,0,0,255))
        panels.append(canvas)
    sheet=Image.new("RGBA",(sum(i.width for i in panels),max(i.height for i in panels)),(255,255,255,255))
    x=0
    for panel in panels:
        sheet.paste(panel,(x,0)); x+=panel.width
    sheet.convert("RGB").save(OUT/f"pikachu_{name.removesuffix('.png')}_compare.png")
