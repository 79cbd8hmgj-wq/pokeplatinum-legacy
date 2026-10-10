#!/usr/bin/env python3
"""Generate DS-sized MO1 V3 decorative panel art, without baked-in item text/icons.

This is source-art preparation. Generated PNG files must be converted through the
repository's actual NCGR/NSCR/NCLR pipeline and tested in an emulator before use.
"""
from argparse import ArgumentParser
from pathlib import Path
from PIL import Image, ImageDraw

W, H = 256, 192
# 16-color maximum including transparent index; intentionally distinct from
# retail Platinum and the rejected neon-tech palette.
COLORS = [
    (0, 0, 0),       # 0 transparent placeholder
    (42, 43, 62),    # mineral ink
    (56, 53, 77),    # framing
    (70, 65, 87),    # raised edge
    (102, 91, 117),  # shadow violet
    (132, 98, 135),  # amethyst edge
    (171, 146, 174), # opalescent transition
    (216, 202, 221), # selected fill
    (240, 233, 236), # secondary pearl
    (250, 246, 244), # primary pearl
    (194, 168, 123), # antique gold
    (142, 165, 165), # opal accent
    (115, 137, 151), # cool shadow
    (222, 214, 216), # panel divider
    (238, 221, 192), # warm tint
    (255, 255, 255), # highlight
]

def draw_panel(d, rect, fill=9, border=5):
    x0,y0,x1,y1=rect
    d.rectangle((x0+3,y0,x1-3,y1), fill=COLORS[border])
    d.rectangle((x0,y0+3,x1,y1-3), fill=COLORS[border])
    d.rectangle((x0+2,y0+4,x1-2,y1-4), fill=COLORS[fill])
    d.line((x0+5,y0+3,x1-5,y0+3),fill=COLORS[15])

def render(screen):
    im=Image.new("RGB",(W,H),COLORS[2])
    d=ImageDraw.Draw(im)
    # Flat, deterministic pixel regions: no baked-in UI copy, item icons or data.
    d.rectangle((0,0,255,9),fill=COLORS[1])
    d.rectangle((0,185,255,191),fill=COLORS[1])
    if screen=="main":
        draw_panel(d,(6,14,249,171),9,4)
        draw_panel(d,(12,21,242,53),8,5)   # reserved item identity header
        draw_panel(d,(12,58,242,127),9,5)   # dynamic description region
        draw_panel(d,(12,132,242,164),8,5)  # context details area
        d.rectangle((17,57,237,58),fill=COLORS[10])
        d.rectangle((17,130,237,131),fill=COLORS[11])
    else:
        draw_panel(d,(5,12,251,182),8,4)
        draw_panel(d,(10,17,246,47),9,5)    # pocket header
        draw_panel(d,(10,52,246,155),9,5)   # active pocket / dial safe region
        draw_panel(d,(10,160,246,177),8,5)  # controller hints
        for x in (24,62,100,138,176,214):
            d.rectangle((x,38,x+16,40),fill=COLORS[10])
    # Indexed palette quantization with a fixed 16-entry DS-compatible palette.
    out=Image.new("P",(W,H))
    palette=[channel for color in COLORS for channel in color]
    out.putpalette(palette+[0]*(768-len(palette)))
    px=out.load()
    rgb=im.load()
    color_index={color:i for i,color in enumerate(COLORS)}
    for y in range(H):
        for x in range(W):
            px[x,y]=color_index[rgb[x,y]]
    return out

def main():
    parser=ArgumentParser()
    parser.add_argument("--output",type=Path,default=Path("build/mo1_bag"))
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    for screen in ("main","sub"):
        image=render(screen)
        assert image.size==(256,192) and image.mode=="P"
        used={v for _,v in image.getcolors(256*192)}
        assert len(used)<=16 and max(used)<16
        filename=args.output/f"opal_v3_{screen}_panel_source.png"
        image.save(filename)
        print(f"{filename}: {len(used)} of 16 palette indices used")
    print("SOURCE ART ONLY — no NARC conversion, game integration or ROM build.")

if __name__=="__main__":
    main()
