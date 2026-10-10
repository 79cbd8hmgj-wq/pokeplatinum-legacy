#!/usr/bin/env python3
"""Rebuild installed Opal MO1 Bag graphics from fixed native tile geometry.

This generator owns the two background tilesets and NSCR maps installed under
res/graphics/bag. The decorative art is NOT the user's V3 mockup as a flat image:
it reserves the real nine-row main-screen list and the sub-screen dial/button
hitbox regions. It must not move gameplay windows or touch targets.

Run --check in CI to prove committed files match generated output.
"""
import argparse
from pathlib import Path
import struct
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"res/graphics/bag"
COLORS=((0,0,0),(250,246,244),(240,233,236),(216,202,221),
        (132,98,135),(56,53,77),(70,65,87),(102,91,117),
        (171,146,174),(194,168,123),(142,165,165),(115,137,151),
        (222,214,216),(238,221,192),(42,43,62),(255,255,255))
TEMPLATE=bytes.fromhex("5243534efffe000124080000100001004e52435314080000000100010000000000080000")

def fill(p,x0,y0,x1,y1,c):
    for y in range(max(0,y0),min(y1,191)+1):
        p[y*256+max(0,x0):y*256+min(x1,255)+1]=[c]*(min(x1,255)-max(0,x0)+1)

def panel(p,x,y,w,h,edge,inside):
    fill(p,x+3,y,x+w-4,y+h-1,edge)
    fill(p,x,y+3,x+w-1,y+h-4,edge)
    fill(p,x+3,y+3,x+w-4,y+h-4,inside)
    fill(p,x+7,y+3,x+w-8,y+3,15)
    fill(p,x+3,y+h-5,x+w-4,y+h-4,12)

def pixels(which):
    p=[5]*(256*192)
    fill(p,0,0,255,8,14)
    fill(p,0,184,255,191,14)
    if which=="main":
        # Existing MAIN BG2 list: x 112..247, y 0..143 (9 rows).
        # Existing MAIN BG0 description: x 0..255, y 144..191.
        # Only decorate the underlying MAIN BG1. Avoid implying the list
        # or description has moved to the other LCD.
        # Opal V3: separated left showcase, legible list rhythm, and
        # bottom description band. BG2 list text and BG0 description
        # windows remain above this decorative BG1 composition.
        panel(p,4,12,104,116,4,2)
        panel(p,112,6,139,150,4,1)
        panel(p,4,147,247,35,4,1)
        # Mineral accent in the showcase and pocket selector footer.
        panel(p,11,19,90,90,7,3)
        fill(p,17,117,94,118,9)
        fill(p,14,121,88,122,12)
        # List header sits above the nine 16-pixel rows; BG2 text is
        # deliberately not overwritten or covered by new windows.
        fill(p,121,9,240,10,9)
        fill(p,121,12,239,13,2)
        for row in range(9):
            y=16+row*16
            fill(p,116,y,246,y+14,1 if row%2==0 else 2)
            fill(p,118,y+2,119,y+12,3)
            fill(p,121,y+15,243,y+15,12)
        # Description area's left item icon and right text gutters.
        fill(p,5,144,252,146,9)
        fill(p,8,152,42,179,2)
        fill(p,43,153,44,177,9)
        fill(p,48,152,238,153,12)
    elif which=="sub":
        p=[0]*(256*192)
        fill(p,0,0,255,8,14)
        fill(p,0,184,255,191,14)
        panel(p,3,12,250,168,4,2)
        panel(p,16,18,224,27,7,1)
        fill(p,16,49,240,51,9)
        # The actual pocket buttons are already rendered on SUB BG0/OAM.
        # Keep BG1 decorative and neutral across 1/4/7/8-pocket contexts.
        # The separately rendered SUB BG3 dial remains functional.
        panel(p,8,30,240,144,7,3)
        fill(p,15,38,240,39,9)
        fill(p,15,165,240,166,9)
        fill(p,57,41,198,161,0)
        fill(p,65,34,190,165,0)
        fill(p,24,175,231,177,9)
    else:
        raise ValueError(which)
    return p

def pack(which):
    pix=pixels(which)
    seen={}
    tiles=[]
    rows=[]
    for ty in range(24):
        row=[]
        for tx in range(32):
            t=tuple(pix[(ty*8+y)*256+tx*8+x] for y in range(8) for x in range(8))
            if t not in seen:
                seen[t]=len(tiles)
                tiles.append(t)
            row.append(seen[t])
        rows.append(row)
    assert len(tiles)<1024
    atlas=Image.new("P",(128,((len(tiles)+15)//16)*8),0)
    palette=[c for rgb in COLORS for c in rgb]
    atlas.putpalette(palette+[0]*(768-len(palette)))
    for i,t in enumerate(tiles):
        tile=Image.new("P",(8,8))
        tile.putdata(t)
        atlas.paste(tile,((i%16)*8,(i//16)*8))
    nscr=bytearray(TEMPLATE)
    for y in range(32):
        for x in range(32):
            nscr+=struct.pack("<H",rows[y][x] if y<24 else 0)
    assert len(nscr)==2084
    return atlas,bytes(nscr)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    for screen,png,map_name in (
        ("main","bag_ui_main_tileset.png","bag_ui_main.NSCR"),
        ("sub","pokeball_borders_tileset.png","pokeball_borders.NSCR")
    ):
        atlas,tilemap=pack(screen)
        import io
        buf=io.BytesIO()
        atlas.save(buf,format="PNG")
        image_path=OUT/png
        map_path=OUT/map_name
        if args.check:
            with Image.open(image_path) as source:
                assert source.mode=="P" and source.size==atlas.size
                assert source.tobytes()==atlas.tobytes(),f"{image_path}: content diverged"
                assert source.getpalette()[:48]==atlas.getpalette()[:48],f"{image_path}: palette diverged"
            assert map_path.read_bytes()==tilemap,f"{map_path}: map diverged"
        else:
            image_path.write_bytes(buf.getvalue())
            map_path.write_bytes(tilemap)
        print(screen,atlas.size, len(tilemap),"CHECK OK" if args.check else "generated")
if __name__=="__main__":
    main()
